from examples.price_api.main import app
from tools.openapi_parser import parse_openapi_document
from tools.patch_generator import generate_payment_patch
from tools.pricing_planner import suggest_pricing


def test_real_mode_env_template_uses_placeholders_only(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=True)

    generate_payment_patch(profile, pricing, tmp_path)

    env_text = tmp_path.joinpath("generated/fastapi/.env.example").read_text(encoding="utf-8")
    assert "OKX_DEVELOPER_API_KEY=replace-with-okx-developer-api-key" in env_text
    assert "OKX_RECIPIENT_WALLET=replace-with-recipient-wallet" in env_text
    assert "OKX_NETWORK=eip155:196" in env_text
    assert "private_key" not in env_text.lower()


def test_real_mode_adapter_exposes_route_config_boundary(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=True)

    generate_payment_patch(profile, pricing, tmp_path)

    adapter = tmp_path.joinpath("generated/fastapi/payment_adapter.py").read_text(encoding="utf-8")
    assert "route_config_preview" in adapter
    assert "OKX_REAL_MODE_NOT_CONFIGURED" in adapter
    assert "OKX_ASSET" in adapter
    assert '"paymentMode": "one_time_exact"' in adapter

