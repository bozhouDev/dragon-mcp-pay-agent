# Dragon MCP Pay Agent

Dragon MCP Pay Agent converts ordinary APIs into paid OKX Marketplace-ready A2MCP services.

This is a contest submission package, not a generic OKR app. The Agent analyzes a FastAPI/OpenAPI service, recommends paid-call pricing, generates payment integration assets, creates marketplace listing files, runs local payment behavior checks, and writes a complete `dist/` package for review.

## Why It Fits OKX

- It helps ASP developers turn existing APIs into paid Marketplace providers.
- It demonstrates Agent Payments Protocol adoption through HTTP 402 behavior, paid-call metadata, and an OKX real-mode adapter boundary.
- It produces reviewable artifacts, not just a chat transcript.
- It can be judged locally without wallet credentials, then configured for real OKX mode when seller prerequisites are available.

## Quick Demo

Install dependencies in your Python 3.11+ environment:

```bash
python3 -m pip install -e ".[dev]"
```

Generate the contest package from the included ordinary FastAPI price API:

```bash
python3 -m apps.cli.onboard onboard \
  --service-path examples/price_api \
  --preferred-path /price \
  --service-name "Token Price API" \
  --price 0.01 \
  --currency USDG \
  --output-dir dist \
  --yes
```

Run the test suite:

```bash
python3 -m pytest -q
```

## Generated Submission Assets

- `dist/payment_patch.diff`
- `dist/services.json`
- `dist/agent_card.json`
- `dist/listing.md`
- `dist/test_report.json`
- `dist/runbook.md`
- `dist/okx_submission_summary.md`
- `dist/service_profile.json`
- `dist/pricing_plan.json`

## Demo Flow

1. Show `examples/price_api/main.py` as a normal API.
2. Run Dragon MCP Pay Agent against that service.
3. Open `dist/service_profile.json` and `dist/pricing_plan.json`.
4. Open `dist/payment_patch.diff`, `dist/services.json`, and `dist/listing.md`.
5. Open `dist/test_report.json` to show unpaid rejection, mock paid success, and invalid-input handling.
6. Finish with `dist/okx_submission_summary.md`.

## Mock Mode And Real OKX Mode

Mock mode is the default because it is reproducible for judges and does not require a wallet, API key, whitelist, or chain transaction. It still proves the payment-gated behavior expected from a paid API conversion: unpaid requests receive payment-required evidence, paid requests reach the business endpoint, and business validation errors remain visible.

Real OKX mode is opt-in and documented in `docs/okx-real-mode.md`. It requires seller credentials, a recipient wallet, broker configuration, network configuration, and an OKX-supported payment asset.

## Project Layout

- `apps/cli/onboard.py`: Typer CLI entrypoint.
- `apps/agent/graph.py`: deterministic onboarding workflow.
- `tools/`: parser, pricing, generators, reports, and tests.
- `templates/`: FastAPI payment assets and listing templates.
- `examples/price_api/`: ordinary FastAPI service used for the contest demo.
- `docs/`: demo script, submission checklist, real-mode notes, and submission summary.
