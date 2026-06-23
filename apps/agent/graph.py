from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from apps.agent.state import WorkflowResult, WorkflowStage, WorkflowState
from tools.listing_generator import generate_listing_assets
from tools.models import ArtifactManifest, REQUIRED_DIST_FILES, PricingPlan, ServiceProfile
from tools.openapi_parser import build_manual_profile, load_openapi_document, parse_openapi_document
from tools.patch_generator import generate_payment_patch
from tools.pricing_planner import suggest_pricing
from tools.repo_scanner import discover_openapi_document
from tools.report_generator import write_submission_reports
from tools.self_test_runner import run_self_tests


class WorkflowError(RuntimeError):
    """Raised when the onboarding workflow cannot continue."""


@dataclass(frozen=True)
class OnboardingRequest:
    service_path: Path | None = None
    openapi_source: str | None = None
    manual_path: str | None = None
    method: str = "GET"
    service_name: str | None = None
    preferred_path: str | None = None
    price: Decimal | str | None = None
    currency: str = "USDG"
    output_dir: Path = Path("dist")
    real_mode: bool = False
    confirmed: bool = False


def run_onboarding(request: OnboardingRequest) -> WorkflowResult:
    state = WorkflowState().with_stage(WorkflowStage.ANALYZE_SERVICE)
    output_dir = request.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = _build_profile(request)
    profile.write_json(output_dir / "service_profile.json")
    state = state.model_copy(update={"service_profile": profile})

    state = state.with_stage(WorkflowStage.PRICING_CONFIRM)
    pricing = _build_pricing(profile, request)
    pricing.write_json(output_dir / "pricing_plan.json")
    state = state.model_copy(update={"pricing_plan": pricing})
    if not pricing.confirmed:
        raise WorkflowError("Pricing must be confirmed before generating payment assets.")

    state = state.with_stage(WorkflowStage.GENERATE_ASSETS)
    generated_paths = []
    generated_paths.extend(generate_payment_patch(profile, pricing, output_dir))
    generated_paths.extend(generate_listing_assets(profile, pricing, output_dir))

    state = state.with_stage(WorkflowStage.SELF_TEST)
    report = run_self_tests(
        profile,
        app_import_path=_app_import_path(request.service_path),
        generated_artifacts=[_relative(output_dir, path) for path in generated_paths],
    )
    report.write_json(output_dir / "test_report.json")

    state = state.with_stage(WorkflowStage.DELIVER)
    write_submission_reports(profile, pricing, report, output_dir)
    manifest = ArtifactManifest.from_output_dir(output_dir, REQUIRED_DIST_FILES)
    manifest.write_json(output_dir / "artifact_manifest.json")
    state = state.model_copy(
        update={
            "artifacts": manifest.generated_files,
        }
    )

    return WorkflowResult(output_dir=str(output_dir), state=state, manifest=manifest)


def _build_profile(request: OnboardingRequest) -> ServiceProfile:
    if request.openapi_source:
        document = load_openapi_document(request.openapi_source)
        return parse_openapi_document(
            document,
            source=request.openapi_source,
            service_name=request.service_name,
            preferred_path=request.preferred_path,
            preferred_method=request.method,
        )

    if request.service_path:
        document, source = discover_openapi_document(request.service_path)
        return parse_openapi_document(
            document,
            source=source,
            service_name=request.service_name,
            preferred_path=request.preferred_path,
            preferred_method=request.method,
        )

    if request.manual_path:
        return build_manual_profile(
            service_name=request.service_name or "Manual API Service",
            endpoint_path=request.manual_path,
            method=request.method,
            source="manual",
            framework="fastapi",
        )

    raise WorkflowError("Provide --service-path, --openapi, or --manual-path.")


def _build_pricing(profile: ServiceProfile, request: OnboardingRequest) -> PricingPlan:
    return suggest_pricing(
        profile,
        amount=request.price,
        currency=request.currency,
        confirmed=request.confirmed,
        real_mode_asset="USDt0",
        real_mode=request.real_mode,
    )


def _app_import_path(service_path: Path | None) -> str | None:
    if service_path is None:
        return None
    path = service_path
    if path.is_dir():
        path = path / "main.py"
    if path.name != "main.py" or not path.exists():
        return None
    try:
        relative = path.with_suffix("").relative_to(Path.cwd())
    except ValueError:
        return None
    return ".".join(relative.parts) + ":app"


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
