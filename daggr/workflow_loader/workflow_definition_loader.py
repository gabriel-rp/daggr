from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from daggr.core.workflow import Workflow


class InvalidWorkflow(Exception):
    def __init__(self, definition: Dict[str, Any], exception: Exception) -> None:
        self.definition = definition
        self.exception = exception

    def __str__(self) -> str:
        return (
            "Workflow cannot be created from definition.\n"
            f"Definition: {self.definition}\n"
            f"Error: {self.exception}"
        )


class InvalidWorkflowSchema(Exception):
    def __init__(self, definition: Dict[str, Any], exception: Exception) -> None:
        self.definition = definition
        self.exception = exception

    def __str__(self) -> str:
        return (
            "Workflow definition has invalid schema.\n"
            f"Definition: {self.definition}\n"
            f"Error: {self.exception}"
        )


class WorkflowDefinitionValidator(ABC):
    filepath: str

    def __init__(self, filepath) -> None:
        self.filepath = filepath

    @abstractmethod
    def validate_schema(self) -> None:
        raise NotImplementedError()


class WorkflowDefinitionLoader(ABC):
    filepath: str
    validator: WorkflowDefinitionValidator

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    @abstractmethod
    def load(self) -> Workflow:
        raise NotImplementedError()
