from __future__ import annotations

import os
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from examples.price_api.main import PRICE_TABLE, PriceResponse


SERVICE_ID = "dragon-mcp-pay-agent"
SERVICE_TITLE = "Dragon MCP Pay Agent"
SERVICE_ENDPOINT = "/price"
DEFAULT_PRICE = "0.01"
DEFAULT_CURRENCY = "USDG"


app = FastAPI(
    title="Dragon MCP Pay Agent A2MCP Provider",
    description=(
        "Public demo endpoint for Dragon MCP Pay Agent. Mock mode proves the paid "
        "request flow until OKX seller credentials are configured."
    ),
    version="0.1.0",
)


def require_payment(
    x_mock_paid: Annotated[str | None, Header(alias="x-mock-paid")] = None,
) -> dict[str, str]:
    mode = os.getenv("DRAGON_PAYMENT_MODE", "mock").lower()
    if mode == "real":
        raise HTTPException(
            status_code=503,
            detail={
                "error": "OKX_REAL_MODE_NOT_CONFIGURED",
                "message": "Set OKX seller SDK credentials before enabling real mode.",
                "requiredEnv": [
                    "OKX_API_KEY",
                    "OKX_SECRET_KEY",
                    "OKX_PASSPHRASE",
                    "PAY_TO_ADDRESS",
                ],
            },
        )

    if x_mock_paid != "true":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "PAYMENT_REQUIRED",
                "serviceId": SERVICE_ID,
                "amount": DEFAULT_PRICE,
                "currency": DEFAULT_CURRENCY,
                "hint": "Retry with x-mock-paid: true for local or contest review.",
            },
            headers={
                "payment-required": (
                    f"service={SERVICE_ID};amount={DEFAULT_PRICE};currency={DEFAULT_CURRENCY}"
                )
            },
        )
    return {"mode": "mock", "serviceId": SERVICE_ID}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_ID}


@app.get("/metadata")
def metadata() -> dict[str, object]:
    return {
        "name": SERVICE_TITLE,
        "serviceType": "A2MCP",
        "endpoint": SERVICE_ENDPOINT,
        "method": "GET",
        "price": DEFAULT_PRICE,
        "currency": DEFAULT_CURRENCY,
        "paymentMode": "one_time_exact",
        "github": "https://github.com/bozhouDev/dragon-mcp-pay-agent",
        "reviewMode": "mock",
    }


@app.get(
    SERVICE_ENDPOINT,
    response_model=PriceResponse,
    dependencies=[Depends(require_payment)],
    summary="Get token price",
    description="Paid demo endpoint for a deterministic token price lookup.",
)
def get_paid_price(
    symbol: str = Query(
        ...,
        pattern=r"^[A-Z0-9]+-[A-Z0-9]+$",
        description="Trading pair such as BTC-USDT.",
        examples=["BTC-USDT"],
    ),
) -> PriceResponse:
    normalized = symbol.upper()
    if normalized not in PRICE_TABLE:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported demo symbol: {normalized}",
        )

    return PriceResponse(
        symbol=normalized,
        price=Decimal(PRICE_TABLE[normalized]),
        quote_currency="USDT",
        source="dragon-mcp-pay-agent-demo",
    )

