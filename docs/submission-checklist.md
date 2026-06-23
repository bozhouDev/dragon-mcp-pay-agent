# Submission Checklist

## Generated Package

- `dist/payment_patch.diff` exists.
- `dist/services.json` exists and validates as JSON.
- `dist/agent_card.json` exists and validates as JSON.
- `dist/listing.md` explains the paid A2MCP provider value.
- `dist/test_report.json` records unpaid, paid, and invalid-input checks.
- `dist/runbook.md` explains how judges can reproduce the demo.
- `dist/okx_submission_summary.md` is ready to paste into submission materials.

## Demo Evidence

- The ordinary `examples/price_api` service runs before payment conversion.
- The Dragon MCP Pay Agent workflow generates all artifacts from that service.
- The mock unpaid request returns payment-required behavior.
- The mock paid request returns a successful business response.
- The demo script stays within 90-120 seconds.

## Safety

- No wallet private keys, API keys, or OKX credentials are committed.
- Real OKX mode is documented as opt-in.
- Mock mode is clearly labeled as local reproducible evidence.

