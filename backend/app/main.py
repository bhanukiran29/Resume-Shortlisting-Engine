import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from root or backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

from backend.app.routes import upload

app = FastAPI(
    title="Resume Matching Engine",
    description="Backend API for parsing, matching, and scoring resumes against job descriptions",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Resume Matching Engine API",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)
