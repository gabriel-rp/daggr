from pathlib import Path
from typing import Any, Dict

import yaml


def write_dict_to_temp_yaml(data: Dict[str, Any], path: Path, filename: str) -> Path:
    filepath = path / "tests" / filename
    filepath.parent.mkdir()
    with open(str(filepath), "w") as f:
        f.write(yaml.dump(data))
    return filepath


def write_str_to_temp_yaml(data: str, path: Path, filename: str) -> Path:
    filepath = path / "tests" / filename
    filepath.parent.mkdir()
    with open(str(filepath), "w") as f:
        f.write(data)
    return filepath
