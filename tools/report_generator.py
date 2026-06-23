from __future__ import annotations

from pathlib import Path

from tools.models import ArtifactManifest, PricingPlan, REQUIRED_DIST_FILES, SelfTestReport, ServiceProfile


def write_submission_reports(
    profile: ServiceProfile,
    pricing: PricingPlan,
    report: SelfTestReport,
    output_dir: str | Path,
) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    manifest = ArtifactManifest.from_output_dir(destination, REQUIRED_DIST_FILES)

    runbook_path = destination / "runbook.md"
    summary_path = destination / "okx_submission_summary.md"
    runbook_path.write_text(_runbook(profile, pricing, report, manifest), encoding="utf-8")
    summary_path.write_text(_summary(profile, pricing, report), encoding="utf-8")
    return [runbook_path, summary_path]


def _runbook(
    profile: ServiceProfile,
    pricing: PricingPlan,
    report: SelfTestReport,
    manifest: ArtifactManifest,
) -> str:
    endpoint = profile.selected_endpoint
    generated = "\n".join(f"- `{item}`" for item in manifest.generated_files)
    missing = "\n".join(f"- `{item}`" for item in manifest.missing_files) or "- None"
    cases = "\n".join(
        f"- {case.name}: {'pass' if case.passed else 'fail'} ({case.status_code})"
        for case in report.cases
    )
    return f"""# Dragon MCP Pay Agent Runbook

## Service

- Name: {profile.service_name}
- Endpoint: `{endpoint.method} {endpoint.path}`
- Price: `{pricing.amount} {pricing.currency}`
- Payment mode: `{pricing.payment_mode}`

## Review Path

1. Inspect the ordinary API profile in `service_profile.json`.
2. Inspect the confirmed pricing in `pricing_plan.json`.
3. Review `payment_patch.diff` and `generated/fastapi/`.
4. Review `services.json`, `agent_card.json`, and `listing.md`.
5. Read `test_report.json` for local payment behavior evidence.

## Generated Files

{generated}

## Missing Required Files

{missing}

## Self-Test Cases

{cases}

## Real OKX Mode

The default package uses mock payment mode for reproducible judging. Real OKX mode requires seller credentials, a recipient wallet, broker configuration, network configuration, and an asset supported by the OKX seller SDK.
"""


def _summary(profile: ServiceProfile, pricing: PricingPlan, report: SelfTestReport) -> str:
    endpoint = profile.selected_endpoint
    return f"""# OKX Submission Summary

## Project

Dragon MCP Pay Agent converts ordinary APIs into paid OKX Marketplace-ready A2MCP provider packages.

## Demo Service

- Source service: {profile.service_name}
- Paid endpoint: `{endpoint.method} {endpoint.path}`
- Price: `{pricing.amount} {pricing.currency}`
- Self-test status: {'passed' if report.overall_passed else 'failed'}

## Why This Should Matter To OKX

The project increases Marketplace supply by helping ASP developers package existing APIs as paid services. It demonstrates Agent Payments Protocol adoption through payment metadata, generated integration assets, local HTTP 402 evidence, mock paid success, and a documented real OKX integration boundary.

## Generated Submission Assets

- `payment_patch.diff`
- `services.json`
- `agent_card.json`
- `listing.md`
- `test_report.json`
- `runbook.md`
"""

