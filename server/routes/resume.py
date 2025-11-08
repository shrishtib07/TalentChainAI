# routes/resume.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from ai_engine import llm_utils
import pypdf
import io

# Create a new router
router = APIRouter(
    prefix="/api/v1/resume",
    tags=["Resume"]  # This will create a new section in your /docs
)

# --- Pydantic Models ---
class ResumeSkillsResponse(BaseModel):
    skills: list[str] = Field(..., example=["Python", "FastAPI", "SQL"])

# --- API Endpoint ---
@router.post("/analyze", response_model=ResumeSkillsResponse)
async def analyze_resume(file: UploadFile = File(...)):
    """
    Analyzes an uploaded resume (PDF) and extracts key technical skills.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Read the file from the upload
        pdf_content = await file.read()
        pdf_stream = io.BytesIO(pdf_content)
        
        # Use pypdf to extract text
        reader = pypdf.PdfReader(pdf_stream)
        resume_text = ""
        for page in reader.pages:
            resume_text += page.extract_text()
            
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # Send the extracted text to our new AI function
        skills_dict = llm_utils.analyze_resume_text(resume_text)
        
        if "error" in skills_dict:
            raise HTTPException(status_code=500, detail=skills_dict["error"])
            
        return skills_dict

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")