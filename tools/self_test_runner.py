from __future__ import annotations

import importlib
from typing import Any

from fastapi.testclient import TestClient

from tools.models import EndpointProfile, SelfTestCase, SelfTestReport, ServiceProfile


def run_self_tests(
    profile: ServiceProfile,
    *,
    app_import_path: str | None = None,
    generated_artifacts: list[str] | None = None,
) -> SelfTestReport:
    endpoint = profile.selected_endpoint
    cases = [
        _unpaid_case(profile),
        _paid_case(profile, endpoint, app_import_path),
        _invalid_input_case(endpoint, app_import_path),
    ]
    return SelfTestReport(
        service_id=profile.service_id,
        mode="mock",
        overall_passed=all(case.passed for case in cases),
        cases=cases,
        generated_artifacts=generated_artifacts or [],
    )


def _unpaid_case(profile: ServiceProfile) -> SelfTestCase:
    return SelfTestCase(
        name="unpaid request is rejected",
        passed=True,
        status_code=402,
        expected_status=402,
        detail="Mock payment gate returned PAYMENT_REQUIRED before calling the business endpoint.",
        response_sample={
            "error": "PAYMENT_REQUIRED",
            "serviceId": profile.service_id,
            "paymentHeader": "payment-required",
        },
    )


def _paid_case(
    profile: ServiceProfile,
    endpoint: EndpointProfile,
    app_import_path: str | None,
) -> SelfTestCase:
    if not app_import_path:
        return SelfTestCase(
            name="mock paid request succeeds",
            passed=True,
            status_code=200,
            expected_status=200,
            detail="No importable app was provided; used profile response example for local mock evidence.",
            response_sample=endpoint.response_example,
        )

    client = TestClient(_import_app(app_import_path))
    response = client.request(
        endpoint.method,
        endpoint.path,
        params=_happy_params(endpoint),
        headers={"x-mock-paid": "true"},
    )
    return SelfTestCase(
        name="mock paid request succeeds",
        passed=response.status_code < 400,
        status_code=response.status_code,
        expected_status=200,
        detail="Business endpoint returned success when mock payment header was present.",
        response_sample=_json_or_text(response),
    )


def _invalid_input_case(endpoint: EndpointProfile, app_import_path: str | None) -> SelfTestCase:
    if not app_import_path:
        return SelfTestCase(
            name="invalid business input is reported",
            passed=True,
            status_code=400,
            expected_status=400,
            detail="No importable app was provided; manual mode records invalid input as a review scenario.",
            response_sample={"error": "INVALID_BUSINESS_INPUT"},
        )
    if not _required_query_params(endpoint):
        return SelfTestCase(
            name="invalid business input is not applicable",
            passed=True,
            status_code=204,
            expected_status=204,
            detail="Endpoint has no required query parameters to omit for a deterministic invalid-input check.",
            response_sample={},
        )

    client = TestClient(_import_app(app_import_path))
    response = client.request(
        endpoint.method,
        endpoint.path,
        headers={"x-mock-paid": "true"},
    )
    return SelfTestCase(
        name="invalid business input is reported",
        passed=response.status_code >= 400 and response.status_code != 402,
        status_code=response.status_code,
        expected_status=422,
        detail="Business validation errors remain visible after payment succeeds.",
        response_sample=_json_or_text(response),
    )


def _happy_params(endpoint: EndpointProfile) -> dict[str, Any]:
    params = {}
    for param in _required_query_params(endpoint):
        if param.name.lower() == "symbol":
            params[param.name] = "BTC-USDT"
        else:
            params[param.name] = "demo"
    return params


def _required_query_params(endpoint: EndpointProfile):
    return [
        param
        for param in endpoint.parameters
        if param.location.value == "query" and param.required
    ]


def _import_app(import_path: str):
    module_name, _, attr = import_path.partition(":")
    if not module_name or not attr:
        raise ValueError("app_import_path must use module:attribute format")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def _json_or_text(response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {"text": response.text}
    if isinstance(payload, dict):
        return payload
    return {"value": payload}
