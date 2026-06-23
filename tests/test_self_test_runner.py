from examples.price_api.main import app
from tools.models import EndpointProfile, ServiceProfile
from tools.openapi_parser import build_manual_profile, parse_openapi_document
from tools.self_test_runner import run_self_tests


def test_self_test_runner_exercises_example_app() -> None:
    profile = parse_openapi_document(app.openapi(), source="example", preferred_path="/price")

    report = run_self_tests(profile, app_import_path="examples.price_api.main:app")

    assert report.overall_passed is True
    assert [case.status_code for case in report.cases] == [402, 200, 422]
    assert report.cases[1].response_sample["symbol"] == "BTC-USDT"


def test_self_test_runner_supports_manual_mode_without_app() -> None:
    profile = build_manual_profile(service_name="Manual API", endpoint_path="/quote")

    report = run_self_tests(profile)

    assert report.overall_passed is True
    assert report.cases[1].status_code == 200
    assert report.cases[2].status_code == 400


def test_invalid_input_case_is_not_applicable_without_required_query_params() -> None:
    endpoint = EndpointProfile(method="GET", path="/openapi.json")
    profile = ServiceProfile.build(
        service_name="Status API",
        source_type="manual",
        source="test",
        framework="fastapi",
        endpoints=[endpoint],
    )

    report = run_self_tests(profile, app_import_path="examples.price_api.main:app")

    assert report.overall_passed is True
    assert report.cases[2].status_code == 204
    assert "not applicable" in report.cases[2].name
