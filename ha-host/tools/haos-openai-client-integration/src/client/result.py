from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerateResult:
    content: str
    data: Any = None
    raw_response: Any = None
    is_structured: bool = False

    @property
    def structured(self) -> bool:
        return self.is_structured
