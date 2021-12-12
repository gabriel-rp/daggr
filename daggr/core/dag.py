from __future__ import annotations

import json
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

from daggr import logger


@dataclass
class WorkflowDefinition:
    dag: str
    steps: Dict[str, Any]
    path: str


class DependenciesNotDefinedYet(Exception):
    def __init__(self, dependency_name: str):
        self.dependency_name = dependency_name

    def __str__(self) -> str:
        return (
            f"The step {self.dependency_name} has not been configured yet.\n"
            "Only after its definition it can be used as a dependency."
        )


class Dag:
    name: str
    root_steps: List[str]
    steps: Dict[str, Step]
    definition_path: str

    def __init__(self, definition: WorkflowDefinition) -> None:
        self.name = definition.dag
        self.root_steps = []
        self.steps = {}
        self.definition_path = definition.path

        for name, data in definition.steps.items():
            data["script"] = data.get("script", name + ".py")
            step = Step(name=name, **data)
            self.steps[name] = step
            if not step.depends_on or len(step.depends_on) == 0:
                self.root_steps.append(name)
            else:
                for dependency_name in step.depends_on:
                    if dependency_name not in self.steps.keys():
                        raise DependenciesNotDefinedYet(dependency_name)
                    self.steps[dependency_name].dependency_of.append(name)


class StepState(Enum):
    WAITING = auto()
    EXECUTING = auto()
    FAILED = auto()
    SUCCESSFUL = auto()
    CANCELLED = auto()


class DagRun:
    dag: Dag
    step_runs: Dict[str, StepRun]

    def __init__(self, dag: Dag) -> None:
        self.dag = dag
        self.step_runs = {}
        for name, step in self.dag.steps.items():
            self.step_runs[name] = StepRun(step)


class StepRun:
    step: Step
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    state: StepState = StepState.WAITING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __init__(self, step: Step):
        self.step = step
        self.stdout = None


class DagRuntime(ABC):
    dag_run: DagRun

    def __init__(self, dag_run: DagRun) -> None:
        self.dag_run = dag_run

    @abstractmethod
    def execute(self):
        raise NotImplementedError()


class LocalRuntime(DagRuntime):
    dag_run: DagRun

    def _start_step_run(self, step_name: str) -> None:
        step_run = self.dag_run.step_runs[step_name]
        step_run.state = StepState.EXECUTING
        step_run.start_time = datetime.utcnow()
        logger.info(f'Executing step "{step_name}".')

    def _end_step_run(
        self, step_name: str, result: subprocess.CompletedProcess
    ) -> None:
        stdout = result.stdout
        stderr = result.stderr

        if result.returncode != 0:
            state = StepState.FAILED
        else:
            state = StepState.SUCCESSFUL

        step_run = self.dag_run.step_runs[step_name]
        step_run.end_time = datetime.utcnow()
        step_run.stdout = stdout
        step_run.stderr = stderr
        step_run.state = state

        logger.info(f'Step "{step_name}" {state}')

    def _create_env(self, step: Step, dag_run: DagRun) -> Dict[str, str]:
        step_name = step.name
        parameters = step.parameters if step.parameters else {}
        inputs = step.inputs if step.inputs else {}

        env = os.environ.copy()
        env["DAGGR_DAG_NAME"] = dag_run.dag.name
        env["DAGGR_STEP_NAME"] = step_name
        env["DAGGR_PARAMETERS"] = json.dumps(parameters)
        env["DAGGR_INPUTS"] = json.dumps(inputs)
        outputs_path = Path(self.dag_run.dag.definition_path) / "outputs"
        outputs_path.mkdir(exist_ok=True)
        env["DAGGR_OUTPUTS_PATH"] = str(outputs_path)

        return env

    def run_step(self, step_name: str) -> StepState:
        self._start_step_run(step_name)

        script_path = str(
            Path(self.dag_run.dag.definition_path)
            / self.dag_run.dag.steps[step_name].script
        )

        result = subprocess.run(
            f"{sys.executable} {script_path}",
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._create_env(self.dag_run.dag.steps[step_name], self.dag_run),
        )

        self._end_step_run(step_name, result)

        return self.dag_run.step_runs[step_name].state

    def run_dependencies_of_step(self, step_name: str):
        for dependent_step in self.dag_run.dag.steps[step_name].dependency_of:
            if self.dag_run.step_runs[dependent_step].state != StepState.WAITING:
                continue

            dependencies_state = self._all_dependencies_are_met(dependent_step)
            if dependencies_state != StepState.SUCCESSFUL:
                continue

            self.run_step_and_dependencies(dependent_step)

    def _all_dependencies_are_met(self, step_name: str) -> StepState:
        for s in self.dag_run.dag.steps[step_name].depends_on:
            dependency_state = self.dag_run.step_runs[s].state
            if dependency_state == StepState.SUCCESSFUL:
                continue
            else:
                return dependency_state
        return StepState.SUCCESSFUL

    def run_step_and_dependencies(self, step_name: str) -> None:
        step_state = self.run_step(step_name)

        if step_state == StepState.SUCCESSFUL:
            self.run_dependencies_of_step(step_name)
        else:
            self.cancel_dependencies_of_step(step_name)

    def cancel_dependencies_of_step(self, step_name: str):
        for step in self.dag_run.dag.steps[step_name].dependency_of:
            self.dag_run.step_runs[step].state = StepState.CANCELLED
            logger.info(f'Step "{step}" {self.dag_run.step_runs[step].state }')

            self.cancel_dependencies_of_step(step)

    def execute(self):
        for root_step in self.dag_run.dag.root_steps:
            self.run_step_and_dependencies(root_step)


class DagRuntimeFactory:
    IMPLEMENTATIONS = {"local": LocalRuntime}

    @staticmethod
    def create(type: str, dag_run: DagRun) -> DagRuntime:
        return DagRuntimeFactory.IMPLEMENTATIONS[type](dag_run)


@dataclass
class Step:
    name: str
    script: str
    depends_on: List[str] = field(default_factory=lambda: [])
    dependency_of: List[str] = field(default_factory=lambda: [])
    parameters: Dict[str, Any] = field(default_factory=lambda: {})
    inputs: Dict[str, Any] = field(default_factory=lambda: {})
    type: str = "python"
    requirements: Optional[str] = None
