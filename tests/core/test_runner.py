from daggr.core.dag import StepState
from daggr.core.runner import Runner


def test_runner():
    r = Runner(
        "yaml", "workflows/examples/simple_workflow/workflow.yml", runtime="local"
    )
    dag_run = r.run()

    for _, step_run in dag_run.step_runs.items():
        assert step_run.state == StepState.SUCCESSFUL
