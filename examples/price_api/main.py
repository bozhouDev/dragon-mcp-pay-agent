from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


class PriceResponse(BaseModel):
    symbol: str = Field(examples=["BTC-USDT"])
    price: Decimal = Field(examples=["64000.50"])
    quote_currency: str = Field(examples=["USDT"])
    source: str = Field(examples=["demo-price-oracle"])


PRICE_TABLE = {
    "BTC-USDT": Decimal("64000.50"),
    "ETH-USDT": Decimal("3200.25"),
    "OKB-USDT": Decimal("50.10"),
}


app = FastAPI(
    title="Token Price API",
    description="A normal price lookup API before Dragon MCP Pay Agent turns it into a paid provider.",
    version="1.0.0",
)


@app.get(
    "/price",
    response_model=PriceResponse,
    summary="Get token price",
    description="Return a deterministic demo price for a crypto trading pair.",
)
def get_price(
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
        price=PRICE_TABLE[normalized],
        quote_currency="USDT",
        source="demo-price-oracle",
    )

