from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Workflow:
    name: str
    steps: List[Any]


@dataclass
class Step:
    name: str
    type: str = "python"
    script: Optional[str] = None
    depends_on: Optional[List[Step]] = None
    parameters: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    requirements: Optional[str] = None
