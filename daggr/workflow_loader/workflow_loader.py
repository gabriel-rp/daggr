from __future__ import annotations

from daggr.core.dag import WorkflowDefinition
from daggr.workflow_loader.workflow_definition_loader import WorkflowDefinitionLoader


class WorkflowLoader:
    def __init__(self, definition_loader: WorkflowDefinitionLoader):
        self.definition_loader = definition_loader

    def load(self) -> WorkflowDefinition:
        return self.definition_loader.load()
