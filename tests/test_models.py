from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.models import (
    ArtifactManifest,
    EndpointProfile,
    PricingPlan,
    REQUIRED_DIST_FILES,
    SelfTestCase,
    SelfTestReport,
    ServiceProfile,
)


def test_service_profile_requires_selected_endpoint_to_be_listed() -> None:
    listed = EndpointProfile(method="GET", path="/price")
    unlisted = EndpointProfile(method="GET", path="/other")

    with pytest.raises(ValidationError):
        ServiceProfile.build(
            service_name="Token Price API",
            source_type="manual",
            source="manual",
            framework="fastapi",
            endpoints=[listed],
            selected_endpoint=unlisted,
        )


def test_pricing_plan_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        PricingPlan(service_id="token-price-api", endpoint_path="/price", amount=Decimal("0"))


def test_json_serialization_is_stable() -> None:
    plan = PricingPlan(
        service_id="token-price-api",
        endpoint_path="/price",
        amount=Decimal("0.01"),
        confirmed=True,
        reasoning=["Low-friction contest demo price."],
    )

    payload = plan.model_dump(mode="json")

    assert payload["amount"] == "0.01"
    assert payload["confirmed"] is True
    assert "generated_at" in payload


def test_manifest_tracks_required_dist_files(tmp_path: Path) -> None:
    (tmp_path / "payment_patch.diff").write_text("diff", encoding="utf-8")
    (tmp_path / "services.json").write_text("{}", encoding="utf-8")

    manifest = ArtifactManifest.from_output_dir(tmp_path, REQUIRED_DIST_FILES)

    assert "payment_patch.diff" in manifest.generated_files
    assert "agent_card.json" in manifest.missing_files
    assert not manifest.all_required_present


def test_self_test_report_overall_must_match_cases() -> None:
    case = SelfTestCase(
        name="unpaid rejected",
        passed=False,
        status_code=200,
        expected_status=402,
        detail="wrong status",
    )

    with pytest.raises(ValidationError):
        SelfTestReport(service_id="token-price-api", overall_passed=True, cases=[case])

