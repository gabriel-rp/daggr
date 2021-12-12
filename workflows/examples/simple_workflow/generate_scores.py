from daggr.core.decorators import output


@output("scores", type="pickle")
def scores():
    scores = {
        "1": {
            "score": 5,
        },
        "2": {
            "score": 7,
        },
        "3": {
            "score": 8,
        },
        "4": {
            "score": 2,
        },
        "5": {
            "score": 1,
        },
        "6": {
            "score": 10,
        },
    }
    return scores


import os

for k, v in os.environ.items():
    if k.startswith("DAGGR"):
        print(f"{k}={v}")
scores()

# @step
# @input(from="step1")
# @output("scores", type="pickle")
# def output(inputs: Dict[str, Any], parameters: Dict[str, Any]):
#     return None

# @output("scores", type="pandas/csv")
# def output(inputs: Dict[str, Any], parameters: Dict[str, Any]):
#     return None


# @output("spark_scores", type="spark/csv")
# def output(inputs: Dict[str, Any], parameters: Dict[str, Any]):
#     return None


# @custom_output("parquet_scores")
# def custom_output(
#     inputs: Dict[str, Any], parameters: Dict[str, Any], path: str, output_name: str
# ):
#     return None

# # daggr run workflow.yml
# #
