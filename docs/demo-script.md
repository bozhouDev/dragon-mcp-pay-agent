# Demo Script

Target length: 90-120 seconds.

## 0-15s: Problem

Most developers already have useful APIs, but turning them into paid OKX Marketplace services still requires protocol understanding, payment integration, listing metadata, and proof that the paid-call path works.

Dragon MCP Pay Agent automates that conversion.

## 15-30s: Ordinary API

Show `examples/price_api/main.py`.

Narration: this is a normal FastAPI token price endpoint, `GET /price?symbol=BTC-USDT`. It has no marketplace listing and no paid-call package.

## 30-55s: Agent Onboarding

Run the CLI against `examples/price_api`.

Narration: the Agent discovers OpenAPI, selects `/price`, recommends a low-friction paid-call price, and confirms the output package.

## 55-80s: Generated Package

Open:

- `dist/service_profile.json`
- `dist/pricing_plan.json`
- `dist/payment_patch.diff`
- `dist/services.json`
- `dist/agent_card.json`
- `dist/listing.md`

Narration: these are the artifacts an ASP developer needs to package a normal API as a paid A2MCP provider.

## 80-105s: Self-Test Evidence

Open `dist/test_report.json`.

Narration: the local review path proves unpaid rejection, mock paid success, and business validation behavior without requiring OKX credentials.

## 105-120s: OKX Value

Open `dist/okx_submission_summary.md`.

Narration: this Agent increases OKX Marketplace supply by helping developers convert existing APIs into paid provider services faster.

