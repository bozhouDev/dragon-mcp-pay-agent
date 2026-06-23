from fastapi.testclient import TestClient

from apps.service.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metadata_endpoint_describes_a2mcp_service() -> None:
    response = client.get("/metadata")

    assert response.status_code == 200
    assert response.json()["serviceType"] == "A2MCP"
    assert response.json()["endpoint"] == "/price"


def test_price_requires_mock_payment_header() -> None:
    response = client.get("/price", params={"symbol": "BTC-USDT"})

    assert response.status_code == 402
    assert response.headers["payment-required"].startswith("service=dragon-mcp-pay-agent")


def test_price_accepts_mock_paid_request() -> None:
    response = client.get(
        "/price",
        params={"symbol": "BTC-USDT"},
        headers={"x-mock-paid": "true"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "symbol": "BTC-USDT",
        "price": "64000.50",
        "quote_currency": "USDT",
        "source": "dragon-mcp-pay-agent-demo",
    }


def test_price_preserves_business_errors_after_payment() -> None:
    response = client.get(
        "/price",
        params={"symbol": "DOGE-USDT"},
        headers={"x-mock-paid": "true"},
    )

    assert response.status_code == 404
