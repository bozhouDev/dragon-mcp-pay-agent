import json

from typer.testing import CliRunner

from apps.cli.onboard import app
from tools.models import REQUIRED_DIST_FILES


runner = CliRunner()


def test_cli_generates_complete_dist_from_example_service(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "onboard",
            "--service-path",
            "examples/price_api",
            "--preferred-path",
            "/price",
            "--service-name",
            "Token Price API",
            "--price",
            "0.01",
            "--currency",
            "USDT",
            "--output-dir",
            str(tmp_path),
            "--yes",
        ],
    )

    assert result.exit_code == 0, result.output
    for required in REQUIRED_DIST_FILES:
        assert tmp_path.joinpath(required).exists(), required
    report = json.loads(tmp_path.joinpath("test_report.json").read_text(encoding="utf-8"))
    assert report["overall_passed"] is True
    assert "Generated contest package" in result.output


def test_cli_declines_without_confirmation(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "onboard",
            "--manual-path",
            "/quote",
            "--service-name",
            "Manual API",
            "--output-dir",
            str(tmp_path),
        ],
        input="n\n",
    )

    assert result.exit_code == 1
    assert not tmp_path.joinpath("payment_patch.diff").exists()


def test_cli_manual_endpoint_mode_generates_package(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "onboard",
            "--manual-path",
            "/quote",
            "--service-name",
            "Manual Market API",
            "--output-dir",
            str(tmp_path),
            "--yes",
        ],
    )

    assert result.exit_code == 0, result.output
    profile = json.loads(tmp_path.joinpath("service_profile.json").read_text(encoding="utf-8"))
    assert profile["source_type"] == "manual"
    assert tmp_path.joinpath("agent_card.json").exists()
