from __future__ import annotations

from decimal import Decimal

from tools.models import PricingPlan, ServiceProfile


def suggest_pricing(
    profile: ServiceProfile,
    *,
    amount: Decimal | str | None = None,
    currency: str = "USDG",
    confirmed: bool = False,
    real_mode_asset: str = "USDt0",
) -> PricingPlan:
    endpoint = profile.selected_endpoint
    suggested_amount = Decimal(str(amount)) if amount is not None else _default_amount(endpoint.method)
    reasoning = [
        f"{endpoint.method} {endpoint.path} is a low-friction API call suitable for a one-time exact payment.",
        "The contest demo price is intentionally small so judges can understand the paid-call flow quickly.",
        "Real OKX mode keeps asset configuration separate from marketplace-facing listing currency.",
    ]
    if profile.source_type == "manual":
        reasoning.append("Manual endpoint mode requires developer confirmation before enabling real payment.")

    return PricingPlan(
        service_id=profile.service_id,
        endpoint_path=endpoint.path,
        amount=suggested_amount,
        currency=currency.upper(),
        payment_mode="one_time_exact",
        real_mode_asset=real_mode_asset,
        confirmed=confirmed,
        reasoning=reasoning,
    )


def _default_amount(method: str) -> Decimal:
    if method.upper() == "GET":
        return Decimal("0.01")
    return Decimal("0.05")

