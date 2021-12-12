from typing import Any, Dict

from daggr.core.decorators import inputs, output

@inputs()
def display(inputs: Dict[str, Any], parameters: Dict[str, Any]):
    print(inputs["approved"])

display()