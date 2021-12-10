import pytest

from daggr.core.dag import WorkflowDefinition
from daggr.workflow_loader.workflow_definition_loader import (
    InvalidWorkflow,
    InvalidWorkflowSchema,
    WorkflowDefinitionLoader,
)
from daggr.workflow_loader.workflow_loader import WorkflowLoader
from daggr.workflow_loader.yaml_definition_loader import (
    CouldNotLoadFile,
    CouldNotParseYaml,
    YamlDefinitionLoader,
    YamlWorkflowValidator,
    _YamlFileLoader,
)
from tests import write_dict_to_temp_yaml, write_str_to_temp_yaml


def test_repr_exceptions():
    str(CouldNotLoadFile("", Exception()))
    str(CouldNotParseYaml("", Exception()))
    str(InvalidWorkflow("", Exception()))
    str(InvalidWorkflowSchema("", Exception()))


def test_valid_yaml_load(tmp_path):
    data = {"a": 10, "b": 20}

    valid_yaml_filepath = write_dict_to_temp_yaml(data, tmp_path, "valid_yaml.yml")
    read_data = _YamlFileLoader.load(str(valid_yaml_filepath))

    assert data == read_data


def test_invalid_path_yaml_load(tmp_path):
    non_existing_filepath = tmp_path / "tests/file.yml"
    with pytest.raises(CouldNotLoadFile):
        _ = _YamlFileLoader.load(str(non_existing_filepath))


def test_invalid_yaml_load(tmp_path, invalid_yaml):
    invalid_yaml_filepath = write_str_to_temp_yaml(
        invalid_yaml, tmp_path, "invalid_yaml.yml"
    )

    with pytest.raises(CouldNotParseYaml):
        _ = _YamlFileLoader.load(str(invalid_yaml_filepath))


def test_yaml_loader_isinstance_of_workflow_loader():
    assert isinstance(YamlDefinitionLoader("file.yml"), WorkflowDefinitionLoader)


def test_yaml_validator_with_non_existing_file():
    with pytest.raises(InvalidWorkflow) as excinfo:
        YamlWorkflowValidator("does_not_exist.yml").validate_schema()
    assert isinstance(excinfo.value.exception, CouldNotLoadFile)


def test_yaml_validator_with_invalid_yaml(tmp_path, invalid_yaml):
    filepath = write_str_to_temp_yaml(invalid_yaml, tmp_path, "invalid_workflow.yml")
    with pytest.raises(InvalidWorkflow) as excinfo:
        YamlWorkflowValidator(filepath).validate_schema()
    assert isinstance(excinfo.value.exception, CouldNotParseYaml)


def test_yaml_validator_with_invalid_workflow_definition(
    tmp_path, invalid_workflow_yaml_definition
):
    filepath = write_str_to_temp_yaml(
        invalid_workflow_yaml_definition, tmp_path, "valid_workflow.yml"
    )
    with pytest.raises(InvalidWorkflowSchema):
        YamlWorkflowValidator(filepath).validate_schema()


def test_yaml_validator_with_valid_yaml(tmp_path, valid_yaml):
    filepath = write_str_to_temp_yaml(valid_yaml, tmp_path, "valid_workflow.yml")
    with pytest.raises(InvalidWorkflowSchema):
        YamlWorkflowValidator(filepath).validate_schema()


def test_loader_with_valid_yaml_definition(valid_workflow_yaml_definition_path):
    loader = YamlDefinitionLoader(valid_workflow_yaml_definition_path)
    workflow = WorkflowLoader(loader).load()
    assert isinstance(workflow, WorkflowDefinition)
