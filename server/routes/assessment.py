# routes/assessment.py

from fastapi import APIRouter
from pydantic import BaseModel, Field
from ai_engine import llm_utils # Import our LLM utility

# Create a router to organize this endpoint
router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment"]
)

# --- Pydantic Models for /generate (Existing) ---
class AssessmentRequest(BaseModel):
    role: str = Field(
        ..., 
        example="Senior Python Developer",
        description="The job role to generate an assessment for."
    )
class AssessmentResponse(BaseModel):
    question: str = Field(..., example="Write a Python function to...")


# --- API Endpoint for /generate (Existing) ---
@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(request: AssessmentRequest):
    question = await llm_utils.generate_assessment_question(request.role)
    return AssessmentResponse(question=question)


# --- --------------------------------------------------- ---
# --- ADD THIS NEW CODE FOR THE /evaluate ENDPOINT ---
# --- --------------------------------------------------- ---

# --- Pydantic Models for /evaluate (New) ---
class EvaluationRequest(BaseModel):
    question: str = Field(..., example="What is a Python decorator?")
    answer: str = Field(..., example="It's a function that takes another function...")
    skill: str = Field(..., example="Python")

class EvaluationResponse(BaseModel):
    score: int = Field(..., example=85)
    level: str = Field(..., example="Intermediate")
    feedback: str = Field(..., example="Good approach, minor syntax issues.")


# --- API Endpoint for /evaluate (New) ---
@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_assessment(request: EvaluationRequest):
    """
    Evaluates a candidate's answer using the AI grader.
    """
    # Call the new AI function from our ai_engine
    evaluation_dict = await llm_utils.evaluate_candidate_answer(
        question=request.question,
        answer=request.answer,
        skill=request.skill
    )
    
    # Return the dictionary, which FastAPI will validate
    # against the EvaluationResponse model.
    return evaluation_dict