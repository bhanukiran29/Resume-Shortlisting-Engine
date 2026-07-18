import os

class ParserService:
    def __init__(self):
        pass

    def parse_resume(self, file_path: str) -> dict:
        """
        Parses resume file and extracts text, contact info, skills, experience, etc.
        Currently a stub.
        """
        filename = os.path.basename(file_path)
        return {
            "filename": filename,
            "extracted_text": f"Stub text extracted from {filename}",
            "skills": ["Stub Skill A", "Stub Skill B"],
            "experience_years": 0.0,
            "education": []
        }

    def parse_job_description(self, text: str) -> dict:
        """
        Parses job description text.
        Currently a stub.
        """
        return {
            "skills_required": ["Stub Skill A"],
            "minimum_experience": 0.0,
            "parsed_title": "Software Engineer"
        }
