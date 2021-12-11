from __future__ import annotations

import json
import os
import pickle
from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple


class output:
    def __init__(self, name: str, type: str, output_path: Optional[str] = None):
        self.name = name
        self.type = type
        self.dag_name = os.getenv("DAGGR_DAG_NAME")
        self.step_name = os.getenv("DAGGR_STEP_NAME", "test")
        if output_path:
            self.output_path = output_path
        else:
            self.output_path = os.getenv("DAGGR_OUTPUTS_PATH")

    def _get_step_output_path(self, step_name: str) -> Path:
        return Path(self.output_path) / step_name

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)

            writer = InterfaceFactory.create(self.type)
            extension = writer.extension()
            step_output_path = self._get_step_output_path(self.step_name)
            step_output_path.mkdir(exist_ok=True)
            writer.write(
                return_value,
                step_output_path / f"{self.name}.{extension}",
            )
            om = OutputMetadata(
                outputs=[OutputInfo(io_interface=self.type, name=self.name)]
            )
            OutputMetadataInterface().write(om, str(step_output_path / ".daggr"))
            return return_value

        return wrapper


class inputs:
    def __init__(self):
        self.parameters = json.loads(os.getenv("DAGGR_PARAMETERS"))
        self.inputs = json.loads(os.getenv("DAGGR_INPUTS"))
        self.dag_name = os.getenv("DAGGR_DAG_NAME")
        self.step_name = os.getenv("DAGGR_STEP_NAME", "test")
        self.output_path = os.getenv("DAGGR_OUTPUTS_PATH")

    def _input_source_is_output(self, input: str) -> bool:
        return input.startswith("output:")

    def _get_step_name(self, input: str) -> str:
        return input.split(":")[1]

    def _get_interface_and_filepath(self, input: str) -> Tuple[str]:
        return input.split(":")[0], input.split(":")[1]

    def _read_metadata_file(self, step_name: str) -> OutputMetadata:
        path = str(self._get_step_output_path(step_name) / ".daggr")
        return OutputMetadataInterface.read(path)

    def _get_step_output_path(self, step_name: str) -> Path:
        return Path(self.output_path) / step_name

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            inputs = {}
            for name, input_definition in self.inputs.items():
                if self._input_source_is_output(input_definition):
                    step_name = self._get_step_name(input_definition)
                    metadata = self._read_metadata_file(step_name)

                    for output in metadata.outputs:
                        io = InterfaceFactory.create(output.io_interface)
                        inputs[name] = io.read(
                            str(
                                self._get_step_output_path(step_name)
                                / f"{output.name}.{io.extension()}"
                            )
                        )
                else:
                    interface, filepath = self._get_interface_and_filepath(input_source)
                    io = InterfaceFactory.create(interface)
                    io.read(filepath)

            return_value = func(
                *args, **kwargs, parameters=self.parameters, inputs=inputs
            )
            return return_value

        return wrapper


class InputReader(ABC):
    def read(self, path: str) -> Any:
        raise NotImplementedError()

    def extension(self) -> str:
        raise NotImplementedError()


class OutputWriter(ABC):
    def write(self, obj: Any, path: str) -> None:
        raise NotImplementedError()

    def extension(self) -> str:
        raise NotImplementedError()


@dataclass
class OutputInfo:
    io_interface: str
    name: str


@dataclass
class OutputMetadata:
    outputs: List[OutputInfo]


class OutputMetadataInterface:
    @staticmethod
    def read(path: str) -> OutputMetadata:
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def write(om: OutputMetadata, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump(om, f)


class IOInterface(InputReader, OutputWriter):
    pass


class PickleInterface(OutputWriter, InputReader):
    def write(self, obj: Any, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump(obj, f)

    def read(self, path: str) -> Any:
        with open(path, "rb") as f:
            return pickle.load(f)

    def extension(self) -> str:
        return "pkl"


class InterfaceNotImplemented(Exception):
    pass


class InterfaceFactory:
    INTERFACES = {"pickle": PickleInterface}

    @staticmethod
    def create(type: str):
        if type not in InterfaceFactory.INTERFACES.keys():
            raise InterfaceNotImplemented()

        return InterfaceFactory.INTERFACES[type]()
