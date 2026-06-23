from examples.price_api.main import app
from tools.openapi_parser import build_manual_profile, parse_openapi_document
from tools.patch_generator import PatchGenerationError, generate_payment_patch
from tools.pricing_planner import suggest_pricing


def test_payment_patch_generates_diff_and_fastapi_assets(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=True)

    paths = generate_payment_patch(profile, pricing, tmp_path)

    assert tmp_path.joinpath("payment_patch.diff").exists()
    assert tmp_path.joinpath("generated/fastapi/payment_adapter.py").exists()
    assert tmp_path.joinpath("generated/fastapi/.env.example").exists()
    assert "Protect GET /price" in tmp_path.joinpath("payment_patch.diff").read_text(encoding="utf-8")
    adapter = tmp_path.joinpath("generated/fastapi/payment_adapter.py").read_text(encoding="utf-8")
    assert "MockPaymentAdapter" in adapter
    assert "OkxPaymentAdapter" in adapter
    assert "replace-with" not in adapter
    assert paths[0].name == "payment_patch.diff"


def test_payment_patch_requires_confirmed_pricing(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=False)

    try:
        generate_payment_patch(profile, pricing, tmp_path)
    except PatchGenerationError as exc:
        assert "Pricing must be confirmed" in str(exc)
    else:  # pragma: no cover - assertion helper
        raise AssertionError("expected PatchGenerationError")


def test_payment_patch_rejects_non_fastapi_framework(tmp_path) -> None:
    profile = build_manual_profile(service_name="Express API", endpoint_path="/quote", framework="express")
    pricing = suggest_pricing(profile, confirmed=True)

    try:
        generate_payment_patch(profile, pricing, tmp_path)
    except PatchGenerationError as exc:
        assert "only supports FastAPI" in str(exc)
    else:  # pragma: no cover - assertion helper
        raise AssertionError("expected PatchGenerationError")

