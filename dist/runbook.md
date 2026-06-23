# Dragon MCP Pay Agent Runbook

## Service

- Name: Token Price API
- Endpoint: `GET /price`
- Price: `0.01 USDG`
- Payment mode: `one_time_exact`
- Intended mode: `mock`

## Review Path

1. Inspect the ordinary API profile in `service_profile.json`.
2. Inspect the confirmed pricing in `pricing_plan.json`.
3. Review `payment_patch.diff` and `generated/fastapi/`.
4. Review `services.json`, `agent_card.json`, and `listing.md`.
5. Read `test_report.json` for local payment behavior evidence.

## Generated Files

- `payment_patch.diff`
- `services.json`
- `agent_card.json`
- `listing.md`
- `test_report.json`
- `runbook.md`
- `okx_submission_summary.md`
- `service_profile.json`
- `pricing_plan.json`

## Missing Required Files

- None

## Self-Test Cases

- unpaid request is rejected: pass (402)
- mock paid request succeeds: pass (200)
- invalid business input is reported: pass (400)

## Real OKX Mode

The default package uses mock payment mode for reproducible judging. Real OKX mode requires seller credentials, a recipient wallet, broker configuration, network configuration, and an asset supported by the OKX seller SDK.
