from typing import List, Optional, Dict
from pydantic import BaseModel


class Field(BaseModel):
    value: str = ""
    confidence: float = 0.0


class Extraction(BaseModel):
    name: Field = Field(default_factory=Field)
    roll_no: Field = Field(default_factory=Field)
    subjects: List[dict] = []               # each: {"subject": "...", "obtained": "...", ...}
    result: Field = Field(default_factory=Field)
    extra: Dict[str, Field] = {}            # board, year, total, etc.
