from typing import Any, Dict

from daggr import Runner, custom_output, output


@output("scores", type="csv")
def output(inputs: Dict[str, Any], parameters: Dict[str, Any]):
    return None


@output("spark_scores", type="spark/csv")
def output(inputs: Dict[str, Any], parameters: Dict[str, Any]):
    return None


@custom_output("parquet_scores")
def custom_output(
    inputs: Dict[str, Any], parameters: Dict[str, Any], path: str, output_name: str
):
    return None


# multiple outputs
Runner().run()  # WORKFLOW_OUTPUT_PATH=outputs/ Runner params
