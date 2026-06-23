from fastapi.testclient import TestClient

from examples.price_api.main import app


client = TestClient(app)


def test_openapi_contains_price_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/price" in response.json()["paths"]


def test_price_happy_path() -> None:
    response = client.get("/price", params={"symbol": "BTC-USDT"})

    assert response.status_code == 200
    assert response.json() == {
        "symbol": "BTC-USDT",
        "price": "64000.50",
        "quote_currency": "USDT",
        "source": "demo-price-oracle",
    }


def test_price_missing_symbol_is_validation_error() -> None:
    response = client.get("/price")

    assert response.status_code == 422


def test_price_unknown_symbol_is_business_error() -> None:
    response = client.get("/price", params={"symbol": "DOGE-USDT"})

    assert response.status_code == 404
    assert "Unsupported demo symbol" in response.json()["detail"]

