from typing import Any, Dict

from daggr.core.decorators import inputs, output


@inputs()
@output("approved", type="pickle")
def filter(inputs: Dict[str, Any], parameters: Dict[str, Any]):
    print("inputs", inputs)
    print("parameters", parameters)
    approved = {
        k: v
        for k, v in inputs["grades"].items()
        if v["score"] >= parameters["passing_score"]
    }
    return approved


filter()
