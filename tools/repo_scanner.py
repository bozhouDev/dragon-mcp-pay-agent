from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from tools.openapi_parser import OpenAPIParserError, load_openapi_document


class ServiceDiscoveryError(ValueError):
    """Raised when a local service cannot be inspected."""


def discover_openapi_document(path: str | Path) -> tuple[dict[str, Any], str]:
    target = Path(path)
    if not target.exists():
        raise ServiceDiscoveryError(f"Service path does not exist: {path}")

    if target.is_file() and target.suffix.lower() == ".json":
        return load_openapi_document(target), str(target)

    if target.is_dir():
        openapi_file = target / "openapi.json"
        if openapi_file.exists():
            return json.loads(openapi_file.read_text(encoding="utf-8")), str(openapi_file)

        main_py = target / "main.py"
        if main_py.exists():
            return _openapi_from_fastapi_module(main_py)

    raise ServiceDiscoveryError(
        "Could not discover OpenAPI. Provide an openapi.json file or use manual endpoint mode."
    )


def _openapi_from_fastapi_module(path: Path) -> tuple[dict[str, Any], str]:
    module_name = f"dragon_discovery_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ServiceDiscoveryError(f"Could not import FastAPI module: {path}")

    parent = str(path.parent)
    sys.path.insert(0, parent)
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - defensive import wrapper
        raise ServiceDiscoveryError(f"Importing {path} failed: {exc}") from exc
    finally:
        sys.modules.pop(module_name, None)
        if sys.path and sys.path[0] == parent:
            sys.path.pop(0)

    app = getattr(module, "app", None)
    if app is None or not hasattr(app, "openapi"):
        raise ServiceDiscoveryError(f"No FastAPI app with openapi() found in {path}")

    try:
        return app.openapi(), f"{path}:app.openapi"
    except OpenAPIParserError:
        raise
    except Exception as exc:  # pragma: no cover - defensive app wrapper
        raise ServiceDiscoveryError(f"Generating OpenAPI from {path} failed: {exc}") from exc
