# routes/assessment.py

from fastapi import APIRouter
from pydantic import BaseModel, Field
from ai_engine import llm_utils # Import our LLM utility

# Create a router to organize this endpoint
router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment"]
)

# --- Pydantic Models ---
# This defines the expected request JSON
class AssessmentRequest(BaseModel):
    role: str = Field(
        ..., 
        example="Senior Python Developer",
        description="The job role to generate an assessment for."
    )

# This defines the response JSON
class AssessmentResponse(BaseModel):
    question: str = Field(..., example="Write a Python function to...")


# --- API Endpoint ---
@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(request: AssessmentRequest):
    """
    Generates a new assessment question based on a job role.
    """
    # Call the AI function from our ai_engine
    question = await llm_utils.generate_assessment_question(request.role)
    
    return AssessmentResponse(question=question)