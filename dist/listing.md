# Token Price API

Token Price API is packaged as an OKX Marketplace A2MCP provider by Dragon MCP Pay Agent.

## Paid API Conversion

- Endpoint: `GET /price`
- Price: `0.01 USDG`
- Payment mode: `one_time_exact`
- Mock review header: `x-mock-paid: true`
- Real mode asset boundary: `USDt0`

## Why It Fits OKX Marketplace

Dragon MCP Pay Agent turns an ordinary API into a paid API conversion package with A2MCP provider metadata, payment integration assets, and self-test evidence. This helps ASP developers list more paid services while keeping the review path reproducible.

## Self-Test Evidence

The generated `test_report.json` records payment-required behavior, mock paid success, and invalid business input handling.
