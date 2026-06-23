from examples.price_api.main import app
from tools.openapi_parser import parse_openapi_document
from tools.pricing_planner import suggest_pricing
from tools.report_generator import write_submission_reports
from tools.self_test_runner import run_self_tests


def test_report_generator_writes_runbook_and_submission_summary(tmp_path) -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")
    pricing = suggest_pricing(profile, confirmed=True)
    report = run_self_tests(profile, app_import_path="examples.price_api.main:app")

    paths = write_submission_reports(profile, pricing, report, tmp_path)

    runbook = tmp_path.joinpath("runbook.md").read_text(encoding="utf-8")
    summary = tmp_path.joinpath("okx_submission_summary.md").read_text(encoding="utf-8")
    assert {path.name for path in paths} == {"runbook.md", "okx_submission_summary.md"}
    assert "Dragon MCP Pay Agent Runbook" in runbook
    assert "Real OKX mode" in runbook
    assert "Missing Required Files" in runbook
    assert "payment_patch.diff" in runbook
    assert "OKX Submission Summary" in summary
    assert "Marketplace supply" in summary
