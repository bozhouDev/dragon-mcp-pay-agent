from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import Header, HTTPException


@dataclass(frozen=True)
class PaymentConfig:
    service_id: str = "token-price-api"
    endpoint_path: str = "/price"
    amount: str = "0.01"
    currency: str = "USDT"
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
        self.api_key = os.getenv("OKX_API_KEY")
        self.secret_key = os.getenv("OKX_SECRET_KEY")
        self.passphrase = os.getenv("OKX_PASSPHRASE")
        self.pay_to_address = os.getenv("PAY_TO_ADDRESS")
        self.base_url = os.getenv("OKX_BASE_URL", "https://web3.okx.com")
        self.network = os.getenv("OKX_PAYMENT_NETWORK", "eip155:196")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.secret_key and self.passphrase and self.pay_to_address)

    def route_config_preview(self) -> dict[str, str]:
        return {
            "serviceId": self.config.service_id,
            "path": self.config.endpoint_path,
            "amount": self.config.amount,
            "currency": self.config.currency,
            "asset": self.config.real_mode_asset,
            "network": self.network,
            "recipient": self.pay_to_address or "PAY_TO_ADDRESS",
            "baseUrl": self.base_url,
            "paymentMode": "one_time_exact",
        }

    def verify(self) -> dict[str, str]:
        if not self.configured:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "OKX_REAL_MODE_UNAVAILABLE",
                    "requiredEnv": [
                        "OKX_API_KEY",
                        "OKX_SECRET_KEY",
                        "OKX_PASSPHRASE",
                        "PAY_TO_ADDRESS",
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
