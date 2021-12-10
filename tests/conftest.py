from pathlib import Path

import pytest
import yaml

from daggr.core.dag import WorkflowDefinition


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


@pytest.fixture
def invalid_workflow_yaml_definition(invalid_workflow_yaml_definition_path):
    with open(invalid_workflow_yaml_definition_path, "r") as f:
        yield f.read()


@pytest.fixture
def workflow_definition():
    yield WorkflowDefinition(
        dag="my_dag",
        steps={"step1": {}, "step2": {"depends_on": ["step1"]}},
        path=str(Path(__file__).parent),
    )


@pytest.fixture
def circular_dependency_definition():
    yield WorkflowDefinition(
        dag="my_dag",
        steps={
            "step_1": {"depends_on": ["step_2"]},
            "step_2": {"depends_on": ["step_1"]},
        },
        path=str(Path(__file__).parent),
    )


@pytest.fixture
def circular_dependency_after_root_definition():
    yield WorkflowDefinition(
        dag="my_dag",
        steps={
            "step_1": {},
            "step_2": {"depends_on": ["step_3"]},
            "step_3": {"depends_on": ["step_2"]},
        },
        path=str(Path(__file__).parent),
    )
