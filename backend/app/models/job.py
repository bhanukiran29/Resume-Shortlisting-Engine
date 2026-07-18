from pydantic import BaseModel, Field
from typing import List

class JobDescription(BaseModel):
    title: str
    description_text: str
    skills_required: List[str] = Field(default_factory=list)
    minimum_experience: float = 0.0
