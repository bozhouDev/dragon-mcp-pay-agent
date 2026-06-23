from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from examples.price_api.main import PRICE_TABLE, PriceResponse


SERVICE_ID = "dragon-mcp-pay-agent"
SERVICE_TITLE = "Dragon MCP Pay Agent"
SERVICE_ENDPOINT = "/price"
DEFAULT_PRICE = "0.01"
DEFAULT_CURRENCY = "USDT"
DEFAULT_NETWORK = "eip155:196"
DEFAULT_BASE_URL = "https://web3.okx.com"
REQUIRED_REAL_ENV = ("OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE", "PAY_TO_ADDRESS")


@dataclass(frozen=True)
class PaymentRuntime:
    mode: str
    okx_enabled: bool
    missing_env: tuple[str, ...] = ()
    error: str | None = None


def payment_mode() -> str:
    return os.getenv("DRAGON_PAYMENT_MODE", "mock").strip().lower()


app = FastAPI(
    title="Dragon MCP Pay Agent A2MCP Provider",
    description=(
        "Public A2MCP endpoint for Dragon MCP Pay Agent. In real mode it protects "
        "the price endpoint with OKX x402 payment verification."
    ),
    version="0.1.0",
)


def configure_okx_payment(fastapi_app: FastAPI) -> PaymentRuntime:
    mode = payment_mode()
    if mode != "real":
        return PaymentRuntime(mode=mode, okx_enabled=False)

    missing = tuple(name for name in REQUIRED_REAL_ENV if not os.getenv(name))
    if missing:
        return PaymentRuntime(mode=mode, okx_enabled=False, missing_env=missing)

    try:
        from x402 import x402ResourceServer
        from x402.http import (
            OKXAuthConfig,
            OKXFacilitatorClient,
            OKXFacilitatorConfig,
            PaymentOption,
            RouteConfig,
        )
        from x402.http.middleware.fastapi import PaymentMiddlewareASGI
        from x402.mechanisms.evm.exact.server import ExactEvmScheme as ExactEvmServerScheme
    except ImportError as exc:
        return PaymentRuntime(mode=mode, okx_enabled=False, error=f"sdk_import_failed: {exc}")

    network = os.getenv("OKX_PAYMENT_NETWORK", DEFAULT_NETWORK)
    pay_to = os.environ["PAY_TO_ADDRESS"]
    price = os.getenv("DRAGON_PAYMENT_PRICE", DEFAULT_PRICE)
    base_url = os.getenv("OKX_BASE_URL", DEFAULT_BASE_URL)
    public_resource = os.getenv("DRAGON_PUBLIC_RESOURCE_URL")

    try:
        facilitator = OKXFacilitatorClient(
            OKXFacilitatorConfig(
                auth=OKXAuthConfig(
                    api_key=os.environ["OKX_API_KEY"],
                    secret_key=os.environ["OKX_SECRET_KEY"],
                    passphrase=os.environ["OKX_PASSPHRASE"],
                ),
                base_url=base_url,
                sync_settle=True,
            )
        )
        server = x402ResourceServer(facilitator)
        server.register(network, ExactEvmServerScheme())
        routes = {
            f"GET {SERVICE_ENDPOINT}": RouteConfig(
                accepts=[
                    PaymentOption(
                        scheme="exact",
                        price=f"${price}",
                        network=network,
                        pay_to=pay_to,
                        max_timeout_seconds=300,
                    )
                ],
                resource=public_resource,
                description="Dragon MCP Pay Agent paid token price lookup",
                mime_type="application/json",
            )
        }
        fastapi_app.add_middleware(
            PaymentMiddlewareASGI,
            routes=routes,
            server=server,
        )
    except Exception as exc:
        return PaymentRuntime(mode=mode, okx_enabled=False, error=f"sdk_config_failed: {exc}")

    return PaymentRuntime(mode=mode, okx_enabled=True)


PAYMENT_RUNTIME = configure_okx_payment(app)


def require_payment(
    x_mock_paid: Annotated[str | None, Header(alias="x-mock-paid")] = None,
) -> dict[str, str]:
    if payment_mode() == "real":
        if PAYMENT_RUNTIME.okx_enabled:
            return {"mode": "real", "serviceId": SERVICE_ID}
        raise HTTPException(
            status_code=503,
            detail={
                "error": "OKX_REAL_MODE_UNAVAILABLE",
                "message": "OKX seller SDK payment middleware is not ready.",
                "missingEnv": list(PAYMENT_RUNTIME.missing_env),
                "runtimeError": PAYMENT_RUNTIME.error,
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
    mode = payment_mode()
    return {
        "name": SERVICE_TITLE,
        "serviceType": "A2MCP",
        "endpoint": SERVICE_ENDPOINT,
        "method": "GET",
        "price": DEFAULT_PRICE,
        "currency": DEFAULT_CURRENCY,
        "network": os.getenv("OKX_PAYMENT_NETWORK", DEFAULT_NETWORK),
        "paymentMode": "one_time_exact",
        "github": "https://github.com/bozhouDev/dragon-mcp-pay-agent",
        "reviewMode": mode,
        "okxPaymentEnabled": PAYMENT_RUNTIME.okx_enabled,
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
