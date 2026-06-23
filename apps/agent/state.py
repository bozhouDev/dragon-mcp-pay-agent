from __future__ import annotations

from enum import Enum
from pathlib import Path

from tools.models import ArtifactManifest, JsonModel, PricingPlan, ServiceProfile


class WorkflowStage(str, Enum):
    COLLECT_INPUT = "collect_input"
    ANALYZE_SERVICE = "analyze_service"
    PRICING_CONFIRM = "pricing_confirm"
    GENERATE_ASSETS = "generate_assets"
    SELF_TEST = "self_test"
    DELIVER = "deliver"
    FAILED = "failed"


class WorkflowState(JsonModel):
    stage: WorkflowStage = WorkflowStage.COLLECT_INPUT
    service_profile: ServiceProfile | None = None
    pricing_plan: PricingPlan | None = None
    artifacts: list[str] = []
    errors: list[str] = []

    def with_stage(self, stage: WorkflowStage) -> WorkflowState:
        return self.model_copy(update={"stage": stage})

    def fail(self, message: str) -> WorkflowState:
        return self.model_copy(update={"stage": WorkflowStage.FAILED, "errors": [*self.errors, message]})


class WorkflowResult(JsonModel):
    output_dir: str
    state: WorkflowState
    manifest: ArtifactManifest

    @property
    def artifact_paths(self) -> list[Path]:
        return [Path(self.output_dir) / item for item in self.manifest.generated_files]

