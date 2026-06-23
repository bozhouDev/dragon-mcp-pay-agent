from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_token_price_api_requires_payment() -> None:
    response = client.get("/price")
    assert response.status_code == 402


def test_token_price_api_accepts_mock_payment() -> None:
    response = client.get(
        "/price",
        headers={"x-mock-paid": "true"},
    )
    assert response.status_code in {200, 422}
