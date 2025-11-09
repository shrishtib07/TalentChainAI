# routes/assessment.py

from fastapi import APIRouter,HTTPException
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


# --- API Endpoint for /generate (NOW FIXED) ---
@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(request: AssessmentRequest):
    """
    Generates a new assessment question based on a job role.
    """
    # Call the AI function from our ai_engine
    question = llm_utils.generate_assessment_question(request.role) # <-- REMOVED AWAIT
    
    return AssessmentResponse(question=question)


# --- --------------------------------------------------- ---
# --- CODE FOR THE /evaluate ENDPOINT ---
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


# --- API Endpoint for /evaluate (NOW FIXED) ---
@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_assessment(request: EvaluationRequest):
    """
    Evaluates a candidate's answer using the AI grader.
    """
    # Call the new AI function from our ai_engine
    evaluation_dict = llm_utils.evaluate_candidate_answer( # <-- REMOVED AWAIT
        question=request.question,
        answer=request.answer,
        skill=request.skill
    )
    
    # Return the dictionary, which FastAPI will validate
    # against the EvaluationResponse model.
    return evaluation_dict

# 1. A model for a single MCQ
class MCQ(BaseModel):
    question: str
    options: list[str] = Field(..., max_items=4)
    correct_answer: str

# 2. The request body our new endpoint will expect
class SkillsRequest(BaseModel):
    skills: list[str] = Field(..., example=["Python", "FastAPI"])

# 3. The final response model with 5 MCQs and 2 coding questions
class QuestionSetResponse(BaseModel):
    mcqs: list[MCQ] = Field(..., max_items=5)
    coding_questions: list[str] = Field(..., max_items=2)

@router.post("/generate_from_skills", response_model=QuestionSetResponse)
async def generate_questions_from_skills(request: SkillsRequest):
    """
    Generates a full set of MCQs and coding questions from a list of skills.
    """
    skills_list = request.skills
    if not skills_list:
        raise HTTPException(status_code=400, detail="No skills provided")

    # Call the new AI function
    question_set_dict = llm_utils.generate_question_set(skills_list)
    
    if "error" in question_set_dict:
        raise HTTPException(status_code=500, detail=question_set_dict["error"])

    # FastAPI will automatically validate the dict against our QuestionSetResponse
    return question_set_dict