# Submission Summary

## Project Name

Dragon MCP Pay Agent

## One-Liner

Dragon MCP Pay Agent converts ordinary APIs into paid OKX Marketplace-ready A2MCP provider packages.

## What It Does

The Agent takes a FastAPI/OpenAPI service, analyzes the endpoint contract, recommends paid-call pricing, generates FastAPI payment integration assets, creates Marketplace listing metadata, runs local payment behavior self-tests, and packages all artifacts under `dist/`.

## Why It Matters

OKX Agent Marketplace needs high-quality paid services. Dragon MCP Pay Agent helps ASP developers bring existing APIs into the Marketplace faster by automating the hardest onboarding steps: protocol packaging, payment-gate assets, listing files, and review evidence.

## Technical Highlights

- FastAPI/OpenAPI service discovery.
- Manual endpoint fallback.
- Pydantic-validated `service_profile.json`, `pricing_plan.json`, `services.json`, `agent_card.json`, and `test_report.json`.
- Mock payment path for reproducible judging.
- Real OKX mode adapter boundary and environment documentation.
- End-to-end Typer CLI workflow.

## Demo Service

The sample converts `examples/price_api` from an ordinary `GET /price` endpoint into a paid provider package with `0.01 USDT` listing price and mock payment evidence.

## Generated Artifacts

- `payment_patch.diff`
- `services.json`
- `agent_card.json`
- `listing.md`
- `test_report.json`
- `runbook.md`
- `okx_submission_summary.md`
