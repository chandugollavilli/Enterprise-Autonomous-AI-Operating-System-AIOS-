import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger("document_intelligence.workflow_engine")


@dataclass
class WorkflowStep:
    step_id: str
    name: str
    action_name: str
    is_optional: bool = False


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    steps: List[WorkflowStep] = field(default_factory=list)


class WorkflowEngine:
    """Configurable Workflow Engine executing document processing pipelines."""

    _workflows: Dict[str, WorkflowDefinition] = {}

    @classmethod
    def register_workflow(cls, workflow: WorkflowDefinition):
        cls._workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered Workflow Pipeline: {workflow.workflow_id} ({len(workflow.steps)} steps)")

    @classmethod
    def get_workflow(cls, workflow_id: str) -> Optional[WorkflowDefinition]:
        return cls._workflows.get(workflow_id)

    @classmethod
    async def execute_workflow(
        cls,
        workflow_id: str,
        context: Dict[str, Any],
        step_handlers: Dict[str, Callable],
    ) -> Dict[str, Any]:
        workflow = cls.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found.")

        start_time = time.perf_counter()
        logger.info(f"Executing Workflow [{workflow.name}] for Document: {context.get('document_id')}")

        executed_steps = []
        for step in workflow.steps:
            handler = step_handlers.get(step.action_name)
            if not handler:
                if step.is_optional:
                    logger.warning(f"Skipping optional unhandled step: {step.name}")
                    continue
                raise ValueError(f"No handler registered for mandatory step action: {step.action_name}")

            step_start = time.perf_counter()
            logger.info(f"Running Workflow Step: [{step.name}]...")
            context = await handler(context)
            step_duration = round((time.perf_counter() - step_start) * 1000, 2)
            executed_steps.append({"step_id": step.step_id, "name": step.name, "duration_ms": step_duration})

        total_duration = round((time.perf_counter() - start_time) * 1000, 2)
        context["_workflow_summary"] = {
            "workflow_id": workflow_id,
            "total_duration_ms": total_duration,
            "steps": executed_steps,
        }
        return context


# Register Default Standard Processing Workflow
standard_pipeline = WorkflowDefinition(
    workflow_id="standard_document_pipeline",
    name="Standard Document Ingestion & OCR Pipeline",
    steps=[
        WorkflowStep("step_1", "Validation & Inspection", "validate_document"),
        WorkflowStep("step_2", "PDF Multi-DPI Rendering", "render_pdf"),
        WorkflowStep("step_3", "Image Preprocessing Plugins", "preprocess_images"),
        WorkflowStep("step_4", "Baidu Unlimited OCR Recognition", "execute_ocr"),
        WorkflowStep("step_5", "Canonical Layout Analysis", "analyze_layout"),
        WorkflowStep("step_6", "Heading-Aware Semantic Chunking", "generate_chunks"),
    ],
)
WorkflowEngine.register_workflow(standard_pipeline)
