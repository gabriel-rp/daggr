import json
from unittest import mock

import pytest

from daggr.core import decorators
from daggr.core.decorators import InterfaceFactory, inputs, output


def test_output_pickle(tmp_path):
    step_name = "pkl_out"
    file = "pickle_file"
    folder = tmp_path
    out = [1, 2, 3]
    with mock.patch.dict(
        decorators.os.environ,
        {
            "DAGGR_DAG_NAME": "test",
            "DAGGR_OUTPUTS_PATH": str(folder),
            "DAGGR_STEP_NAME": step_name,
        },
    ):

        @output(file, type="pickle")
        def test():
            return out

        test()

        assert (
            InterfaceFactory.create("pickle").read(f"{folder / step_name / file}.pkl")
            == out
        )


def test_empty_outputs_path():
    with mock.patch.dict(decorators.os.environ, {}, clear=True):
        with pytest.raises(Exception):

            @output("pickle_file", type="pickle")
            def test():
                return []

            test()


def test_input(tmp_path):
    dag = "test"
    output_folder = tmp_path
    output_step_name = "pkl_out"
    input_step_name = "pkl_in"
    base_filename = "pickle_file"
    io_interface = "pickle"

    out = [1, 2, 3]

    with mock.patch.dict(
        decorators.os.environ,
        {
            "DAGGR_DAG_NAME": dag,
            "DAGGR_OUTPUTS_PATH": str(output_folder),
            "DAGGR_STEP_NAME": output_step_name,
        },
    ):

        @output(base_filename, type=io_interface)
        def write_output():
            return out

        write_output()

    with mock.patch.dict(
        decorators.os.environ,
        {
            "DAGGR_DAG_NAME": dag,
            "DAGGR_STEP_NAME": input_step_name,
            "DAGGR_OUTPUTS_PATH": str(output_folder),
            "DAGGR_PARAMETERS": json.dumps({"answer": 42}),
            "DAGGR_INPUTS": json.dumps({"input1": f"output:{output_step_name}"}),
        },
    ):

        @inputs()
        def read_input(inputs, parameters):
            assert inputs["input1"] == out
            assert parameters["answer"] == 42

        read_input()


def test_outputs_path_parameter_override(tmp_path):
    step_name = "pkl_out"
    file = "pickle_file"

    env_output_folder = tmp_path / "env"
    env_output_folder.mkdir()
    param_output_folder = tmp_path / "param"
    param_output_folder.mkdir()

    out = [1, 2, 3]
    with mock.patch.dict(
        decorators.os.environ,
        {
            "DAGGR_DAG_NAME": "test",
            "DAGGR_OUTPUTS_PATH": str(env_output_folder),
            "DAGGR_STEP_NAME": step_name,
        },
    ):

        @output(file, type="pickle", output_path=str(param_output_folder))
        def test():
            return out

        test()

    assert (
        InterfaceFactory.create("pickle").read(
            f"{param_output_folder / step_name / file}.pkl"
        )
        == out
    )

    with pytest.raises(Exception):
        assert (
            InterfaceFactory.create("pickle").read(
                f"{env_output_folder / step_name / file}.pkl"
            )
            == out
        )
