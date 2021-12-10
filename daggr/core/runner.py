from daggr.core.dag import Dag, DagRun, DagRuntimeFactory
from daggr.workflow_loader.workflow_definition_loader_factory import (
    WorkflowDefinitionLoaderFactory,
)
from daggr.workflow_loader.workflow_loader import WorkflowLoader


class Runner:
    def __init__(self, workflow_format: str, workflow_filepath: str, runtime: str):
        self.workflow_format = workflow_format
        self.workflow_filepath = workflow_filepath
        self.runtime = runtime

    def run(self) -> DagRun:
        definition_loader = WorkflowDefinitionLoaderFactory.create(
            self.workflow_format, self.workflow_filepath
        )
        loader = WorkflowLoader(definition_loader)
        wd = loader.load()
        dag = Dag(wd)
        dag_run = DagRun(dag)
        runtime = DagRuntimeFactory.create(self.runtime, dag_run)
        runtime.execute()

        return dag_run
