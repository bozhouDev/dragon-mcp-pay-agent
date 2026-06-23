from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from apps.agent.graph import OnboardingRequest, WorkflowError, run_onboarding
from apps.agent.prompts import CONFIRM_PRICING_PROMPT, DEFAULT_MANUAL_PATH, DEFAULT_SERVICE_NAME


app = typer.Typer(help="Dragon MCP Pay Agent contest package generator.")


@app.callback()
def main() -> None:
    """Generate OKX Marketplace-ready paid provider packages."""


@app.command()
def onboard(
    service_path: Optional[Path] = typer.Option(
        None,
        "--service-path",
        help="Local FastAPI service directory or OpenAPI JSON file.",
    ),
    openapi_source: Optional[str] = typer.Option(
        None,
        "--openapi",
        help="OpenAPI JSON file or URL.",
    ),
    manual_path: Optional[str] = typer.Option(
        None,
        "--manual-path",
        help="Manual endpoint path when no OpenAPI document is available.",
    ),
    method: str = typer.Option("GET", "--method", help="HTTP method for preferred/manual endpoint."),
    preferred_path: Optional[str] = typer.Option(
        None,
        "--preferred-path",
        help="Endpoint path to package when the service has multiple endpoints.",
    ),
    service_name: Optional[str] = typer.Option(None, "--service-name", help="Marketplace service name."),
    price: Optional[str] = typer.Option(None, "--price", help="Price per paid call."),
    currency: str = typer.Option("USDG", "--currency", help="Marketplace-facing listing currency."),
    output_dir: Path = typer.Option(Path("dist"), "--output-dir", help="Generated package output directory."),
    real_mode: bool = typer.Option(False, "--real-mode", help="Document real OKX mode as the intended adapter path."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm pricing and generation non-interactively."),
) -> None:
    if service_path is None and openapi_source is None and manual_path is None:
        manual_path = typer.prompt("Endpoint path", default=DEFAULT_MANUAL_PATH)
    if service_name is None and manual_path is not None:
        service_name = typer.prompt("Service name", default=DEFAULT_SERVICE_NAME)

    confirmed = yes or typer.confirm(CONFIRM_PRICING_PROMPT, default=True)
    if not confirmed:
        typer.echo("Pricing not confirmed; no payment package generated.", err=True)
        raise typer.Exit(code=1)

    request = OnboardingRequest(
        service_path=service_path,
        openapi_source=openapi_source,
        manual_path=manual_path,
        method=method,
        service_name=service_name,
        preferred_path=preferred_path,
        price=price,
        currency=currency,
        output_dir=output_dir,
        real_mode=real_mode,
        confirmed=confirmed,
    )
    try:
        result = run_onboarding(request)
    except WorkflowError as exc:
        typer.echo(f"Workflow failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Generated contest package: {result.output_dir}")
    for artifact in result.manifest.generated_files:
        typer.echo(f"- {artifact}")


if __name__ == "__main__":
    app()
