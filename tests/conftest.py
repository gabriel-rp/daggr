from pathlib import Path

import pytest
import yaml


@pytest.fixture
def invalid_yaml():
    yield """"
a: 10
b:
  - 1
   - 2
  - 3
"""


@pytest.fixture
def valid_yaml():
    yield yaml.dump({"a": 20, "b": 10})


@pytest.fixture
def valid_workflow_yaml_definition_path():
    yield str(Path(__file__).parent / "valid_workflow.yml")


@pytest.fixture
def invalid_workflow_yaml_definition_path():
    yield str(Path(__file__).parent / "invalid_workflow.yml")


# @pytest.fixture
# def valid_workflow_yaml_definition(valid_workflow_yaml_definition_path):
#     with open(valid_workflow_yaml_definition_path, "r") as f:
#         yield f.read()


@pytest.fixture
def invalid_workflow_yaml_definition(invalid_workflow_yaml_definition_path):
    with open(invalid_workflow_yaml_definition_path, "r") as f:
        yield f.read()
