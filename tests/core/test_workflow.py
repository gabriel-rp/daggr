import pytest

from daggr.core.workflow import Step, Workflow


def test_empty_workflow():
    with pytest.raises(Exception):
        Workflow()


def test_empty_step():
    with pytest.raises(Exception):
        Step()


def test_valid_step():
    Step(name="my_step")


def test_valid_workflow():
    Workflow(name="my_workflow", steps=[Step(name="my_step")])
