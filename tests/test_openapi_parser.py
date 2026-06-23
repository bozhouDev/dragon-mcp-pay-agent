from examples.price_api.main import app
from tools.openapi_parser import build_manual_profile, parse_openapi_document
from tools.repo_scanner import discover_openapi_document


def test_parse_fastapi_openapi_document() -> None:
    profile = parse_openapi_document(
        app.openapi(),
        source="examples/price_api",
        preferred_path="/price",
    )

    assert profile.service_name == "Token Price API"
    assert profile.service_id == "token-price-api"
    assert profile.selected_endpoint.method == "GET"
    assert profile.selected_endpoint.path == "/price"
    assert profile.selected_endpoint.parameters[0].name == "symbol"
    assert profile.selected_endpoint.response_example["symbol"] == "BTC-USDT"


def test_manual_endpoint_fallback_profile() -> None:
    profile = build_manual_profile(
        service_name="Manual Market API",
        endpoint_path="quote",
        query_parameters=["symbol", "venue"],
    )

    assert profile.source_type == "manual"
    assert profile.selected_endpoint.path == "/quote"
    assert [param.name for param in profile.selected_endpoint.parameters] == ["symbol", "venue"]
    assert profile.risks


def test_repo_scanner_discovers_fastapi_app_openapi() -> None:
    document, source = discover_openapi_document("examples/price_api")

    assert source.endswith("main.py:app.openapi")
    assert document["info"]["title"] == "Token Price API"
    assert "/price" in document["paths"]

