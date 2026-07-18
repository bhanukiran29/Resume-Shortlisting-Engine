from pydantic import BaseModel
from backend.app.models.resume import ParsedResume

class ScoredCandidate(BaseModel):
    resume: ParsedResume
    score: float
    matched_skills: list
    missing_skills: list
    rank: int = 1
