from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import Header, HTTPException


@dataclass(frozen=True)
class PaymentConfig:
    service_id: str = "token-price-api"
    endpoint_path: str = "/price"
    amount: str = "0.01"
    currency: str = "USDG"
    real_mode_asset: str = "USDt0"


class MockPaymentAdapter:
    def __init__(self, config: PaymentConfig) -> None:
        self.config = config

    def verify(self, paid_header: str | None) -> dict[str, str]:
        if paid_header != "true":
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "PAYMENT_REQUIRED",
                    "serviceId": self.config.service_id,
                    "amount": self.config.amount,
                    "currency": self.config.currency,
                    "hint": "Retry with x-mock-paid: true for local review.",
                },
                headers={
                    "payment-required": (
                        f"service={self.config.service_id};"
                        f"amount={self.config.amount};"
                        f"currency={self.config.currency}"
                    )
                },
            )
        return {"mode": "mock", "serviceId": self.config.service_id, "paid": "true"}


class OkxPaymentAdapter:
    def __init__(self, config: PaymentConfig) -> None:
        self.config = config
        self.developer_api_key = os.getenv("OKX_DEVELOPER_API_KEY")
        self.recipient_wallet = os.getenv("OKX_RECIPIENT_WALLET")
        self.broker_base_url = os.getenv("OKX_BROKER_BASE_URL")

    @property
    def configured(self) -> bool:
        return bool(self.developer_api_key and self.recipient_wallet and self.broker_base_url)

    def route_config_preview(self) -> dict[str, str]:
        return {
            "serviceId": self.config.service_id,
            "path": self.config.endpoint_path,
            "amount": self.config.amount,
            "currency": self.config.currency,
            "asset": os.getenv("OKX_ASSET", self.config.real_mode_asset),
            "network": os.getenv("OKX_NETWORK", "eip155:196"),
            "recipient": self.recipient_wallet or "OKX_RECIPIENT_WALLET",
            "paymentMode": "one_time_exact",
        }

    def verify(self) -> dict[str, str]:
        if not self.configured:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "OKX_REAL_MODE_NOT_CONFIGURED",
                    "requiredEnv": [
                        "OKX_DEVELOPER_API_KEY",
                        "OKX_RECIPIENT_WALLET",
                        "OKX_BROKER_BASE_URL",
                    ],
                },
            )
        return {"mode": "real-boundary", "serviceId": self.config.service_id}


CONFIG = PaymentConfig()
MOCK_ADAPTER = MockPaymentAdapter(CONFIG)
OKX_ADAPTER = OkxPaymentAdapter(CONFIG)


async def require_payment(
    x_mock_paid: str | None = Header(default=None, alias="x-mock-paid"),
) -> dict[str, str]:
    if os.getenv("DRAGON_PAYMENT_MODE", "mock").lower() == "real":
        return OKX_ADAPTER.verify()
    return MOCK_ADAPTER.verify(x_mock_paid)