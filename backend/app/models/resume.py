from pydantic import BaseModel, Field
from typing import List, Optional

class ParsedResume(BaseModel):
    filename: str
    extracted_text: str
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: List[str] = Field(default_factory=list)
    contact_info: Optional[dict] = None
