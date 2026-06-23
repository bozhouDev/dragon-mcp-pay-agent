# OKX Real Mode

Dragon MCP Pay Agent defaults to mock payment mode so the contest demo is reproducible without wallet credentials, API keys, whitelist state, or chain transactions.

Real OKX mode is an opt-in adapter boundary for sellers who have the required OKX setup.

## Required Seller Inputs

- `OKX_DEVELOPER_API_KEY`
- `OKX_RECIPIENT_WALLET`
- `OKX_BROKER_BASE_URL`
- `OKX_NETWORK`
- `OKX_ASSET`
- Target paid endpoint path and method
- Confirmed price and payment mode

## Generated Environment Template

The generator writes `dist/generated/fastapi/.env.example` with placeholders only. It must never contain real credentials.

## Route Config Shape

Generated assets preserve the fields needed by an OKX seller integration boundary:

- service id
- endpoint path
- amount
- marketplace-facing currency
- real-mode asset
- recipient wallet
- network
- broker base URL

## Default Review Path

Judges should use mock mode for local review:

- unpaid request: payment-required behavior
- mock paid request: business endpoint success
- invalid business input: business validation remains visible

## Official References

- OKX Agent Payments Protocol: `https://web3.okx.com/onchainos/dev-docs/payments/app`
- OKX Agent Payments overview: `https://web3.okx.com/onchainos/dev-docs/payments/overview`
- OKX Seller SDK integration: `https://web3.okx.com/onchainos/dev-docs/payments/service-seller-sdk`
- OKX payments SDK repository: `https://github.com/okx/payments`

