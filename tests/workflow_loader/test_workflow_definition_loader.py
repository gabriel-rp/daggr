import pytest

from daggr.core.dag import WorkflowDefinition
from daggr.workflow_loader.workflow_definition_loader import (
    WorkflowDefinitionLoader,
    WorkflowDefinitionValidator,
)


def test_abstract_workflow_validator(valid_workflow_yaml_definition_path):
    with pytest.raises(TypeError):
        WorkflowDefinitionValidator(valid_workflow_yaml_definition_path)


def test_abstract_workflow_loader(valid_workflow_yaml_definition_path):
    with pytest.raises(TypeError):
        WorkflowDefinitionLoader(valid_workflow_yaml_definition_path)


def test_incomplete_validator_implementation(valid_workflow_yaml_definition_path):
    class IncompleteValidator(WorkflowDefinitionValidator):
        def validate_schema(self) -> None:
            return super().validate_schema()

    with pytest.raises(NotImplementedError):
        IncompleteValidator(valid_workflow_yaml_definition_path).validate_schema()


def test_incomplete_loader_implementation(valid_workflow_yaml_definition_path):
    class IncompleteLoader(WorkflowDefinitionLoader):
        def load(self) -> WorkflowDefinition:
            return super().load()

    with pytest.raises(NotImplementedError):
        IncompleteLoader(valid_workflow_yaml_definition_path).load()
