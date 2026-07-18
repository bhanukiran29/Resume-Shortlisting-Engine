import os
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.app.services.parser import ParserService

router = APIRouter()
parser_service = ParserService()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate file type (e.g., PDF or DOCX)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT are supported.")

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    safe_filename = Path(file.filename).name
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Call the parser
    try:
        parsed_data = parser_service.parse_resume(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    return {
        "message": "File uploaded and parsed successfully",
        "file_path": file_path,
        "parsed_data": parsed_data
    }
