from decimal import Decimal

from examples.price_api.main import app
from tools.openapi_parser import build_manual_profile, parse_openapi_document
from tools.pricing_planner import suggest_pricing


def test_default_get_pricing_is_low_friction() -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")

    plan = suggest_pricing(profile, confirmed=True)

    assert plan.amount == Decimal("0.01")
    assert plan.currency == "USDG"
    assert plan.payment_mode == "one_time_exact"
    assert plan.intended_mode == "mock"
    assert plan.confirmed is True
    assert plan.real_mode_asset == "USDt0"


def test_user_can_override_price_and_currency() -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")

    plan = suggest_pricing(profile, amount="0.25", currency="usdt", confirmed=True)

    assert plan.amount == Decimal("0.25")
    assert plan.currency == "USDT"


def test_manual_mode_reasoning_mentions_confirmation() -> None:
    profile = build_manual_profile(service_name="Manual API", endpoint_path="/quote")

    plan = suggest_pricing(profile)

    assert plan.confirmed is False
    assert any("Manual endpoint" in item for item in plan.reasoning)


def test_real_mode_request_is_recorded_in_pricing_plan() -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")

    plan = suggest_pricing(profile, confirmed=True, real_mode=True)

    assert plan.intended_mode == "real-boundary"
    assert any("Real OKX mode" in item for item in plan.reasoning)
