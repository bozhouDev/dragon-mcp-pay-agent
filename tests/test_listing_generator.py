import json

from examples.price_api.main import app
from tools.listing_generator import generate_listing_assets
from tools.openapi_parser import parse_openapi_document
from tools.pricing_planner import suggest_pricing


def test_listing_generator_writes_marketplace_assets(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=True)

    paths = generate_listing_assets(profile, pricing, tmp_path)

    services = json.loads(tmp_path.joinpath("services.json").read_text(encoding="utf-8"))
    agent_card = json.loads(tmp_path.joinpath("agent_card.json").read_text(encoding="utf-8"))
    listing = tmp_path.joinpath("listing.md").read_text(encoding="utf-8")

    assert {path.name for path in paths} == {"services.json", "agent_card.json", "listing.md"}
    assert services["marketplace"] == "OKX Agent Marketplace"
    assert services["services"][0]["endpoint"] == "/price"
    assert services["services"][0]["payment"]["mockHeader"] == "x-mock-paid: true"
    assert agent_card["agent_id"] == "dragon-mcp-pay-agent"
    assert "OKX Marketplace" in listing
    assert "A2MCP provider" in listing
    assert "paid API conversion" in listing
    assert "self-test evidence" in listing

