# Dragon MCP Pay Agent

Dragon MCP Pay Agent converts ordinary APIs into paid OKX Marketplace-ready A2MCP services.

It is built as a contest submission package, not a generic OKR app. The workflow analyzes a FastAPI/OpenAPI service, recommends pricing, generates payment integration assets, creates marketplace listing files, runs local payment behavior checks, and writes a complete `dist/` package for review.

## What It Produces

- `dist/payment_patch.diff`
- `dist/services.json`
- `dist/agent_card.json`
- `dist/listing.md`
- `dist/test_report.json`
- `dist/runbook.md`
- `dist/okx_submission_summary.md`
- `dist/service_profile.json`
- `dist/pricing_plan.json`

## Demo Shape

The included example starts from a normal token price API and turns it into a paid provider package. The stable demo path uses mock payment behavior so judges can verify HTTP 402 and paid-success flows without OKX credentials. Real OKX mode is documented separately and remains opt-in.

## Project Layout

- `apps/cli/onboard.py`: Typer CLI entrypoint.
- `apps/agent/graph.py`: deterministic onboarding workflow.
- `tools/`: parser, pricing, generators, reports, and tests.
- `examples/price_api/`: ordinary FastAPI service used for the contest demo.
- `docs/`: demo script, submission checklist, and OKX real-mode notes.

