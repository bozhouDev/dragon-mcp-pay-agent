from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from tools.models import (
    EndpointParameter,
    EndpointProfile,
    ParameterLocation,
    ServiceProfile,
)


HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


class OpenAPIParserError(ValueError):
    """Raised when an OpenAPI document cannot produce a service profile."""


def load_openapi_document(source: str | Path) -> dict[str, Any]:
    source_text = str(source)
    if source_text.startswith(("http://", "https://")):
        response = httpx.get(source_text, timeout=10.0)
        response.raise_for_status()
        return response.json()

    path = Path(source)
    if not path.exists():
        raise OpenAPIParserError(f"OpenAPI source does not exist: {source}")
    if path.is_dir():
        path = path / "openapi.json"
    return json.loads(path.read_text(encoding="utf-8"))


def parse_openapi_document(
    openapi: dict[str, Any],
    *,
    source: str,
    service_name: str | None = None,
    preferred_path: str | None = None,
    preferred_method: str | None = None,
) -> ServiceProfile:
    if "paths" not in openapi:
        raise OpenAPIParserError("OpenAPI document is missing paths")

    endpoints = _extract_endpoints(openapi)
    if not endpoints:
        raise OpenAPIParserError("OpenAPI document has no supported HTTP endpoints")

    selected = _select_endpoint(endpoints, preferred_path, preferred_method)
    if selected is None:
        raise OpenAPIParserError("Preferred endpoint was not found in OpenAPI document")

    title = service_name or openapi.get("info", {}).get("title") or "API Service"
    auth_assumptions = _auth_assumptions(openapi, selected)
    risks = [
        "Mock payment proves local behavior; real OKX mode requires seller credentials and wallet configuration.",
    ]
    if not openapi.get("components", {}).get("securitySchemes"):
        risks.append("No existing auth scheme detected; payment gate becomes the first access-control layer.")

    return ServiceProfile.build(
        service_name=title,
        source_type="openapi",
        source=source,
        framework="fastapi",
        endpoints=endpoints,
        selected_endpoint=selected,
        auth_assumptions=auth_assumptions,
        risks=risks,
    )


def build_manual_profile(
    *,
    service_name: str,
    endpoint_path: str,
    method: str = "GET",
    source: str = "manual",
    framework: str = "fastapi",
    query_parameters: list[str] | None = None,
) -> ServiceProfile:
    params = [
        EndpointParameter(
            name=name,
            location=ParameterLocation.QUERY,
            required=True,
            schema_type="string",
            description=f"Manual query parameter: {name}",
        )
        for name in (query_parameters or ["symbol"])
    ]
    endpoint = EndpointProfile(
        method=method,
        path=endpoint_path,
        operation_id=f"manual_{method.lower()}_{endpoint_path.strip('/').replace('/', '_') or 'root'}",
        summary=f"Manual endpoint for {service_name}",
        parameters=params,
        response_schema={"type": "object"},
        response_example={"symbol": "BTC-USDT", "price": "64000.50", "source": "manual-example"},
    )
    return ServiceProfile.build(
        service_name=service_name,
        source_type="manual",
        source=source,
        framework=framework,
        endpoints=[endpoint],
        selected_endpoint=endpoint,
        auth_assumptions=["Manual endpoint mode: existing authentication was not inspected."],
        risks=["Manual mode depends on the developer confirming endpoint shape before real OKX mode."],
    )


def _extract_endpoints(openapi: dict[str, Any]) -> list[EndpointProfile]:
    endpoints = []
    for path, path_item in openapi.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            endpoints.append(_endpoint_from_operation(openapi, path, method, operation))
    return endpoints


def _endpoint_from_operation(
    openapi: dict[str, Any],
    path: str,
    method: str,
    operation: dict[str, Any],
) -> EndpointProfile:
    parameters = []
    for item in operation.get("parameters", []):
        schema = item.get("schema", {})
        parameters.append(
            EndpointParameter(
                name=item["name"],
                location=ParameterLocation(item.get("in", "query")),
                required=item.get("required", False),
                schema_type=schema.get("type", "string"),
                description=item.get("description", ""),
            )
        )

    response_schema = _response_schema(openapi, operation)
    return EndpointProfile(
        method=method,
        path=path,
        operation_id=operation.get("operationId"),
        summary=operation.get("summary", ""),
        parameters=parameters,
        response_schema=response_schema,
        response_example=_example_from_schema(response_schema),
    )


def _response_schema(openapi: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    responses = operation.get("responses", {})
    success = responses.get("200") or responses.get("201") or {}
    content = success.get("content", {})
    media = content.get("application/json") or next(iter(content.values()), {})
    schema = media.get("schema", {})
    return _resolve_ref(openapi, schema)


def _resolve_ref(openapi: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        return schema
    name = ref.removeprefix(prefix)
    return openapi.get("components", {}).get("schemas", {}).get(name, schema)


def _example_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    if not schema:
        return {}
    if schema.get("type") != "object":
        return {"value": _example_value("value", schema)}

    example = {}
    for name, property_schema in schema.get("properties", {}).items():
        example[name] = _example_value(name, property_schema)
    return example


def _example_value(name: str, schema: dict[str, Any]) -> Any:
    if "examples" in schema and schema["examples"]:
        return schema["examples"][0]
    field_type = schema.get("type", "string")
    normalized_name = name.lower()
    if normalized_name == "symbol":
        return "BTC-USDT"
    if normalized_name == "price":
        return "64000.50"
    if normalized_name == "quote_currency":
        return "USDT"
    if normalized_name == "source":
        return "demo-price-oracle"
    if field_type in {"number", "integer"}:
        return 1
    if field_type == "boolean":
        return True
    if field_type == "array":
        return []
    if field_type == "object":
        return {}
    return "string"


def _select_endpoint(
    endpoints: list[EndpointProfile],
    preferred_path: str | None,
    preferred_method: str | None,
) -> EndpointProfile | None:
    method = preferred_method.upper() if preferred_method else None
    if preferred_path:
        normalized_path = preferred_path if preferred_path.startswith("/") else f"/{preferred_path}"
        for endpoint in endpoints:
            if endpoint.path == normalized_path and (method is None or endpoint.method == method):
                return endpoint
        return None

    for endpoint in endpoints:
        if endpoint.method == "GET":
            return endpoint
    return endpoints[0]


def _auth_assumptions(openapi: dict[str, Any], endpoint: EndpointProfile) -> list[str]:
    security_schemes = openapi.get("components", {}).get("securitySchemes", {})
    if security_schemes:
        names = ", ".join(sorted(security_schemes))
        return [f"Existing OpenAPI security schemes detected: {names}."]
    return [f"No existing auth scheme detected for {endpoint.method} {endpoint.path}."]

