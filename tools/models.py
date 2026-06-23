from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    cleaned = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("-")
            previous_dash = True
    return "".join(cleaned).strip("-") or "service"


class JsonModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def json_text(self) -> str:
        return self.model_dump_json(indent=2)

    def write_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.json_text() + "\n", encoding="utf-8")
        return path


class ParameterLocation(str, Enum):
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    BODY = "body"


class EndpointParameter(JsonModel):
    name: str
    location: ParameterLocation = ParameterLocation.QUERY
    required: bool = False
    schema_type: str = "string"
    description: str = ""


class EndpointProfile(JsonModel):
    method: str
    path: str
    operation_id: str | None = None
    summary: str = ""
    parameters: list[EndpointParameter] = Field(default_factory=list)
    response_schema: dict[str, Any] = Field(default_factory=dict)
    response_example: dict[str, Any] = Field(default_factory=dict)

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        method = value.upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError(f"unsupported HTTP method: {value}")
        return method

    @field_validator("path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        if not value.startswith("/"):
            return f"/{value}"
        return value


class ServiceProfile(JsonModel):
    service_name: str
    service_id: str
    source_type: Literal["openapi", "manual", "repo"]
    source: str
    framework: str = "fastapi"
    selected_endpoint: EndpointProfile
    endpoints: list[EndpointProfile]
    auth_assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def selected_endpoint_must_be_listed(self) -> ServiceProfile:
        if not self.endpoints:
            raise ValueError("at least one endpoint is required")
        selected_key = (self.selected_endpoint.method, self.selected_endpoint.path)
        endpoint_keys = {(item.method, item.path) for item in self.endpoints}
        if selected_key not in endpoint_keys:
            raise ValueError("selected endpoint must be included in endpoints")
        return self

    @classmethod
    def build(
        cls,
        service_name: str,
        source_type: Literal["openapi", "manual", "repo"],
        source: str,
        framework: str,
        endpoints: list[EndpointProfile],
        selected_endpoint: EndpointProfile | None = None,
        auth_assumptions: list[str] | None = None,
        risks: list[str] | None = None,
    ) -> ServiceProfile:
        selected = selected_endpoint or endpoints[0]
        return cls(
            service_name=service_name,
            service_id=slugify(service_name),
            source_type=source_type,
            source=source,
            framework=framework,
            endpoints=endpoints,
            selected_endpoint=selected,
            auth_assumptions=auth_assumptions or [],
            risks=risks or [],
        )


class PricingPlan(JsonModel):
    service_id: str
    endpoint_path: str
    amount: Decimal = Decimal("0.01")
    currency: str = "USDG"
    payment_mode: Literal["one_time_exact"] = "one_time_exact"
    intended_mode: Literal["mock", "real-boundary"] = "mock"
    real_mode_asset: str = "USDt0"
    confirmed: bool = False
    reasoning: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("amount must be positive")
        return value


class ServiceListing(JsonModel):
    service_id: str
    name: str
    description: str
    endpoint: str
    method: str
    price: str
    currency: str
    payment_mode: str
    capabilities: list[str]
    payment: dict[str, Any]


class ServicesDocument(JsonModel):
    version: str = "1.0"
    marketplace: str = "OKX Agent Marketplace"
    services: list[ServiceListing]


class AgentCard(JsonModel):
    name: str
    agent_id: str
    description: str
    version: str = "0.1.0"
    capabilities: list[str]
    inputs: list[str]
    outputs: list[str]
    okx_fit: list[str]


class ArtifactManifest(JsonModel):
    output_dir: str
    required_files: list[str]
    generated_files: list[str]
    missing_files: list[str] = Field(default_factory=list)

    @property
    def all_required_present(self) -> bool:
        return not self.missing_files

    @classmethod
    def from_output_dir(cls, output_dir: Path, required_files: list[str]) -> ArtifactManifest:
        generated = []
        missing = []
        for relative in required_files:
            path = output_dir / relative
            if path.exists():
                generated.append(relative)
            else:
                missing.append(relative)
        return cls(
            output_dir=str(output_dir),
            required_files=required_files,
            generated_files=generated,
            missing_files=missing,
        )


class SelfTestCase(JsonModel):
    name: str
    passed: bool
    status_code: int
    expected_status: int
    detail: str
    response_sample: dict[str, Any] = Field(default_factory=dict)


class SelfTestReport(JsonModel):
    service_id: str
    mode: Literal["mock", "real-boundary"] = "mock"
    overall_passed: bool
    cases: list[SelfTestCase]
    generated_artifacts: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def overall_matches_cases(self) -> SelfTestReport:
        expected = all(case.passed for case in self.cases)
        if self.overall_passed != expected:
            raise ValueError("overall_passed must match case results")
        return self


REQUIRED_DIST_FILES = [
    "payment_patch.diff",
    "services.json",
    "agent_card.json",
    "listing.md",
    "test_report.json",
    "runbook.md",
    "okx_submission_summary.md",
    "service_profile.json",
    "pricing_plan.json",
]
