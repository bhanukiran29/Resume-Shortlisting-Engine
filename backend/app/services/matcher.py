class MatcherService:
    def __init__(self):
        pass

    def match_resume_to_job(self, parsed_resume: dict, parsed_job: dict) -> dict:
        """
        Matches resume skills and requirements with job description.
        Currently a stub.
        """
        matched_skills = list(set(parsed_resume.get("skills", [])) & set(parsed_job.get("skills_required", [])))
        return {
            "matched_skills": matched_skills,
            "missing_skills": list(set(parsed_job.get("skills_required", [])) - set(parsed_resume.get("skills", []))),
            "experience_match": parsed_resume.get("experience_years", 0) >= parsed_job.get("minimum_experience", 0)
        }
