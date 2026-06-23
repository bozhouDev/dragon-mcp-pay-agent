import json
from pathlib import Path

from apps.agent.graph import OnboardingRequest, run_onboarding
from tools.models import REQUIRED_DIST_FILES


def test_submission_package_contains_required_files(tmp_path) -> None:
    result = run_onboarding(
        OnboardingRequest(
            service_path=Path("examples/price_api"),
            preferred_path="/price",
            service_name="Token Price API",
            price="0.01",
            currency="USDG",
            output_dir=tmp_path,
            confirmed=True,
        )
    )

    assert result.manifest.all_required_present
    for required in REQUIRED_DIST_FILES:
        assert tmp_path.joinpath(required).exists(), required

    report = json.loads(tmp_path.joinpath("test_report.json").read_text(encoding="utf-8"))
    assert report["overall_passed"] is True


def test_readme_and_submission_docs_name_okx_marketplace() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    demo_script = Path("docs/demo-script.md").read_text(encoding="utf-8")
    summary = Path("docs/submission-summary.md").read_text(encoding="utf-8")

    assert "OKX Marketplace-ready A2MCP" in readme
    assert "90-120 seconds" in demo_script
    assert "ASP developers" in summary

