from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

from daggr.core.dag import (
    Dag,
    DagRun,
    DagRuntime,
    DagRuntimeFactory,
    DependenciesNotDefinedYet,
    DependencyOnSelfNotAllowed,
    LocalRuntime,
    Step,
    StepState,
    WorkflowDefinition,
)
from daggr.core.dag import subprocess as dag_subprocess


def test_empty_workflow():
    with pytest.raises(Exception):
        WorkflowDefinition()


def test_empty_step():
    with pytest.raises(Exception):
        Step()


def test_valid_step():
    Step(name="mystep", script="my/step.py", inputs={"l": []})


def test_valid_workflow():
    WorkflowDefinition(
        dag="my_workflow", steps={"my_step": None}, path=str(Path(__file__).parent)
    )


def test_dag(workflow_definition):
    Dag(definition=workflow_definition)


def test_exceptions_repr():
    str(DependenciesNotDefinedYet(""))
    str(DependencyOnSelfNotAllowed(""))


def test_step_name_is_used_when_no_script_name():
    step_name = "my_step"
    wd = WorkflowDefinition(dag="test", steps={step_name: {}}, path="file/path")
    dag = Dag(wd)
    assert dag.steps[step_name].script == step_name + ".py"


def test_script_name_when_set():
    step_name = "my_step"
    script = "my/script.py"
    wd = WorkflowDefinition(
        dag="test", steps={step_name: {"script": script}}, path="file/path"
    )
    dag = Dag(wd)

    assert dag.steps[step_name].name == step_name
    assert dag.steps[step_name].script == script


def test_dag_with_circular_dependency(circular_dependency_definition):
    with pytest.raises(DependenciesNotDefinedYet):
        Dag(definition=circular_dependency_definition)


def test_dag_with_circular_dependency_after_root(
    circular_dependency_after_root_definition,
):
    with pytest.raises(DependenciesNotDefinedYet):
        Dag(definition=circular_dependency_after_root_definition)


def test_dagrun_initial_state_is_waiting(workflow_definition):
    dag = Dag(workflow_definition)
    dagrun = DagRun(dag)
    for _, step_run in dagrun.step_runs.items():
        assert step_run.state == StepState.WAITING


def test_incomplete_dag_runtime_class(workflow_definition):
    class IncompleteRuntime(DagRuntime):
        def execute(self):
            super().execute()

    with pytest.raises(NotImplementedError):
        dag = Dag(workflow_definition)
        dagrun = DagRun(dag)
        runtime = IncompleteRuntime(dagrun)
        runtime.execute()


def test_step_execution():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test": {"script": "step_test.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.run_step("step_test")
    assert runtime.dag_run.step_runs["step_test"].stdout == "Hello World\n"


def test_step_execution_time():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test": {"script": "step_test.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    step = runtime.dag_run.step_runs["step_test"]

    assert step.start_time is None
    assert step.end_time is None

    before = datetime.utcnow()
    runtime.run_step("step_test")
    after = datetime.utcnow()

    assert step.start_time > before
    assert step.start_time < after
    assert step.end_time > before
    assert step.end_time < after
    assert step.start_time < step.end_time


def test_multiple_steps_executed():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "step1": {"script": "step_test.py"},
            "step2": {"script": "step_test.py", "depends_on": ["step1"]},
        },
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)

    step1 = runtime.dag_run.step_runs["step1"]
    step2 = runtime.dag_run.step_runs["step2"]

    runtime.execute()

    assert step1.start_time is not None
    assert step1.end_time is not None
    assert step2.start_time is not None
    assert step2.end_time is not None


def test_dag_with_local_runtime():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test": {"script": "step_test.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )

    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)

    runtime.run_step = mock.MagicMock(return_value=None)
    runtime.execute()

    runtime.run_step.assert_called_once()


def test_dag_with_non_existing_file():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test_with_error": {"script": "file_that_does_not_exist.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )

    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()
    assert dagrun.step_runs["step_test_with_error"].state == StepState.FAILED


def test_dag_with_error():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test_with_error": {"script": "step_test_with_error.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )

    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()
    assert dagrun.step_runs["step_test_with_error"].state == StepState.FAILED


def test_dag_with_no_dependencies():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step1": {}},
        path="my/path",
    )
    dag = Dag(wd)
    assert len(dag.steps["step1"].depends_on) == 0


def test_dag_with_no_dependents():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step1": {}},
        path="my/path",
    )
    dag = Dag(wd)
    assert len(dag.steps["step1"].dependency_of) == 0


def test_dag_with_parameters():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step_test": {"script": "step_with_parameters.py"}},
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.run_step("step_test")
    assert dagrun.step_runs["step_test"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step_test"].stdout == ""


def test_step_runs_after_dependency():
    wd = WorkflowDefinition(
        dag="test_dag",
        steps={"step1": {}, "step2": {"depends_on": ["step1"]}},
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()
    assert dagrun.step_runs["step1"].end_time < dagrun.step_runs["step2"].start_time


class MockedSuccessfulRun:
    stdout = ""
    stderr = ""
    returncode = 0
    state = StepState.SUCCESSFUL


class MockedFailedRun:
    stdout = ""
    stderr = "error"
    returncode = 1
    state = StepState.FAILED


def test_multiple_steps_run_in_correct_order():
    dag_subprocess.run = mock.MagicMock(return_value=MockedSuccessfulRun())

    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "step1": {},
            "step2": {"depends_on": ["step1"]},
            "step3": {"depends_on": ["step1"]},
            "step4": {"depends_on": ["step2"]},
            "step5": {"depends_on": ["step4"]},
        },
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()

    assert dagrun.step_runs["step1"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step2"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step3"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step4"].state == StepState.SUCCESSFUL

    assert dagrun.step_runs["step1"].end_time < dagrun.step_runs["step2"].start_time
    assert dagrun.step_runs["step1"].end_time < dagrun.step_runs["step3"].start_time
    assert dagrun.step_runs["step2"].end_time < dagrun.step_runs["step4"].start_time
    assert dagrun.step_runs["step4"].end_time < dagrun.step_runs["step5"].start_time


def test_redundant_dependencies():
    dag_subprocess.run = mock.MagicMock(return_value=MockedSuccessfulRun())

    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "root": {},
            "step1": {"depends_on": ["root"]},
            "step2": {"depends_on": ["root", "step1"]},
            "step3": {"depends_on": ["root", "step1", "step2"]},
        },
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()

    runtime.run_step = mock.MagicMock(return_value=MockedSuccessfulRun())

    assert dagrun.step_runs["root"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step1"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step2"].state == StepState.SUCCESSFUL
    assert dagrun.step_runs["step3"].state == StepState.SUCCESSFUL

    assert dagrun.step_runs["root"].end_time < dagrun.step_runs["step1"].start_time
    assert dagrun.step_runs["step1"].end_time < dagrun.step_runs["step2"].start_time
    assert dagrun.step_runs["step2"].end_time < dagrun.step_runs["step3"].start_time


def test_failed_dependency_cancels_downstream():

    dag_subprocess.run = mock.MagicMock(return_value=MockedFailedRun())

    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "root": {},
            "step1": {"depends_on": ["root"]},
            "step2": {"depends_on": ["step1"]},
            "step3": {"depends_on": ["step2"]},
        },
        path=str(Path(__file__).parent / "scripts"),
    )
    dag = Dag(wd)
    dagrun = DagRun(dag)
    runtime = LocalRuntime(dagrun)
    runtime.execute()

    assert dagrun.step_runs["root"].state == StepState.FAILED
    assert dagrun.step_runs["step1"].state == StepState.CANCELLED
    assert dagrun.step_runs["step2"].state == StepState.CANCELLED
    assert dagrun.step_runs["step3"].state == StepState.CANCELLED


def test_dependency_on_itself():
    dag_subprocess.run = mock.MagicMock(return_value=MockedSuccessfulRun())

    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "root": {"depends_on": ["root"]},
        },
        path=str(Path(__file__).parent / "scripts"),
    )
    with pytest.raises(DependencyOnSelfNotAllowed):
        dag = Dag(wd)


def test_runtime_factory():
    dag_subprocess.run = mock.MagicMock(return_value=MockedSuccessfulRun())

    wd = WorkflowDefinition(
        dag="test_dag",
        steps={
            "root": {},
        },
        path="",
    )
    dag = Dag(wd)
    dag_run = DagRun(dag)

    impl = "local"
    runtime = DagRuntimeFactory.create(impl, dag_run)
    assert runtime.dag_run == dag_run
    assert isinstance(runtime, DagRuntimeFactory.IMPLEMENTATIONS[impl])
