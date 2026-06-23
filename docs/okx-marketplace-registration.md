# OKX Marketplace A2MCP ASP Registration Packet

## Registration Status

Status: Public HTTPS demo endpoint is deployed. Manual portal submission is ready after OKX seller credentials are available.

Onchain OS CLI 3.3.13 does not expose a public `register marketplace` or `register asp` command. The current Onchain OS payment docs say sellers can load the Payment SDK into a DApp/MCP service and start charging without payment-gateway registration, while Marketplace listing itself appears to be handled through OKX web surfaces or manual review.

## ASP / Provider

- Provider name: Dragon MCP Pay Agent
- Service type: A2MCP
- Category: Developer tooling / Agent payments / Marketplace onboarding
- GitHub: https://github.com/bozhouDev/dragon-mcp-pay-agent
- Submission zip: `dragon-mcp-pay-agent-submission.zip`
- Primary contact: to be filled in OKX portal

## Service Listing

- Service title: Dragon MCP Pay Agent
- Service subtitle: Convert ordinary APIs into paid OKX Marketplace-ready A2MCP provider packages.
- Demo service: Token Price API
- Endpoint path: `GET /price`
- Public endpoint URL: `https://aitoday.xin/dragon-mcp/price`
- Price: `0.01 USDT`
- Payment mode: `one_time_exact`
- Real-mode asset boundary: `USDt0`
- Network: X Layer, `eip155:196`

## Description

Dragon MCP Pay Agent helps ASP developers bring more paid services to OKX Agent Marketplace. It analyzes a FastAPI/OpenAPI service, recommends paid-call pricing, generates payment integration assets, creates Marketplace listing files, runs local payment behavior checks, and packages all artifacts under `dist/`.

The submitted package includes mock payment evidence for reproducible review and an opt-in real OKX mode boundary for sellers with Developer Portal credentials and a recipient wallet.

## Capabilities

- Analyze FastAPI/OpenAPI services.
- Build `service_profile.json` from OpenAPI or manual endpoint input.
- Recommend paid-call pricing.
- Generate FastAPI payment adapter assets.
- Generate A2MCP-ready `services.json`, `agent_card.json`, and listing copy.
- Run local self-tests for unpaid rejection, mock paid success, and invalid business input.
- Produce an OKX submission summary and runbook.

## Evidence

- `dist/services.json`
- `dist/agent_card.json`
- `dist/listing.md`
- `dist/test_report.json`
- `dist/runbook.md`
- `dist/okx_submission_summary.md`
- `docs/demo-script.md`
- `docs/okx-real-mode.md`

## Required Before Marketplace Listing

- Public HTTPS endpoint URL for the A2MCP service: `https://aitoday.xin/dragon-mcp/price`
- Recipient wallet address.
- OKX Developer Portal API key, secret key, and passphrase.
- Real OKX seller SDK configuration in the deployed backend.
- OKX portal/manual review submission.

## Recommended Submission Copy

Dragon MCP Pay Agent converts ordinary APIs into paid OKX Marketplace-ready A2MCP provider packages. It helps ASP developers analyze an existing service, define pricing, generate payment assets, create listing metadata, run payment behavior self-tests, and submit a reviewable package. This increases Marketplace supply by reducing the work required to turn normal APIs into paid agent-callable services.
