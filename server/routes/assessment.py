# routes/assessment.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from ai_engine import llm_utils
import uuid # 1. Import for generating unique IDs

# 2. Create the router. We can't set the prefix/tags here anymore.
router = APIRouter()

# --- Existing Models for /generate ---
class AssessmentRequest(BaseModel):
    role: str = Field(..., example="Senior Python Developer")
class AssessmentResponse(BaseModel):
    question: str = Field(..., example="Write a Python function to...")

# --- Existing Endpoint /generate ---
@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(request: AssessmentRequest):
    question = llm_utils.generate_assessment_question(request.role)
    return AssessmentResponse(question=question)

# --- Existing Models for /evaluate ---
class EvaluationRequest(BaseModel):
    question: str
    answer: str
    skill: str
class EvaluationResponse(BaseModel):
    score: int
    level: str
    feedback: str

# --- Existing Endpoint /evaluate ---
@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_assessment(request: EvaluationRequest):
    evaluation_dict = llm_utils.evaluate_candidate_answer(
        question=request.question,
        answer=request.answer,
        skill=request.skill
    )
    return evaluation_dict

# --- --------------------------------------------------- ---
# --- MODELS FOR "GENERATE FROM SKILLS" & "SUBMIT"
# --- --------------------------------------------------- ---

# --- Pydantic Models for Question Set ---
class MCQ(BaseModel):
    question: str
    options: list[str] = Field(..., max_items=4)
    correct_answer: str # This will be stored on the server

class FullQuestionSet(BaseModel): # This is the full model with answers
    mcqs: list[MCQ]
    coding_questions: list[str]

class SkillsRequest(BaseModel):
    skills: list[str] = Field(..., example=["Python", "FastAPI"])

# 3. This is the SANITIZED response we send to the frontend (no answers)
class SanitizedMCQ(BaseModel):
    question: str
    options: list[str]

class QuestionSetResponse(BaseModel):
    test_id: str
    mcqs: list[SanitizedMCQ]
    coding_questions: list[str]

# --- --------------------------------------------------- ---
# --- ENDPOINT: /generate_from_skills (UPDATED)
# --- --------------------------------------------------- ---

@router.post("/generate_from_skills", response_model=QuestionSetResponse)
async def generate_questions_from_skills(request: Request, skills_request: SkillsRequest):
    skills_list = skills_request.skills
    if not skills_list:
        raise HTTPException(status_code=400, detail="No skills provided")

    question_set_data = llm_utils.generate_question_set(skills_list)
    if "error" in question_set_data:
        raise HTTPException(status_code=500, detail=question_set_data["error"])

    # 4. Validate the full set of questions (with answers)
    try:
        full_test = FullQuestionSet(**question_set_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid data: {e}")

    # 5. Create a unique ID and store the full test in the "cache"
    test_id = str(uuid.uuid4())
    request.app.state.test_cache[test_id] = full_test

    # 6. Create the "sanitized" list of MCQs to send to the user
    sanitized_mcqs = [
        SanitizedMCQ(question=mcq.question, options=mcq.options) for mcq in full_test.mcqs
    ]

    # 7. Return the sanitized test and the new test_id
    return QuestionSetResponse(
        test_id=test_id,
        mcqs=sanitized_mcqs,
        coding_questions=full_test.coding_questions
    )

# --- --------------------------------------------------- ---
# --- NEW ENDPOINT: /submit
# --- --------------------------------------------------- ---

# 8. Models for the submission
class UserMCQAnswer(BaseModel):
    question: str
    answer: str

class TestSubmissionRequest(BaseModel):
    test_id: str
    mcq_answers: list[UserMCQAnswer]
    coding_answers: list[str]

class GradedMCQ(BaseModel):
    question: str
    your_answer: str
    correct_answer: str
    is_correct: bool

class TestResultResponse(BaseModel):
    mcq_score: str
    mcq_results: list[GradedMCQ]
    coding_results: list[EvaluationResponse]

@router.post("/submit", response_model=TestResultResponse)
async def submit_test(request: Request, submission: TestSubmissionRequest):
    # 9. Get the correct answers from our cache
    full_test = request.app.state.test_cache.get(submission.test_id)
    if not full_test:
        raise HTTPException(status_code=404, detail="Test ID not found or expired.")

    # 10. Grade the MCQs
    mcq_results = []
    correct_count = 0
    # Create a simple lookup map of the correct answers
    correct_answer_map = {mcq.question: mcq.correct_answer for mcq in full_test.mcqs}

    for mcq_answer in submission.mcq_answers:
        is_correct = False
        correct_answer = correct_answer_map.get(mcq_answer.question, "N/A")
        if mcq_answer.answer == correct_answer:
            is_correct = True
            correct_count += 1
        
        mcq_results.append(GradedMCQ(
            question=mcq_answer.question,
            your_answer=mcq_answer.answer,
            correct_answer=correct_answer,
            is_correct=is_correct
        ))
    
    mcq_score = f"{correct_count} / {len(full_test.mcqs)}"

    # 11. Grade the Coding Questions using the AI
    coding_results = []
    for i, code_answer in enumerate(submission.coding_answers):
        question = full_test.coding_questions[i]
        # Call our existing AI evaluator
        evaluation = llm_utils.evaluate_candidate_answer(
            question=question,
            answer=code_answer,
            skill="Coding" # General skill
        )
        coding_results.append(EvaluationResponse(**evaluation))

    # 12. Delete the test from the cache
    try:
        del request.app.state.test_cache[submission.test_id]
    except KeyError:
        pass # Already gone, no problem

    # 13. Return the final results
    return TestResultResponse(
        mcq_score=mcq_score,
        mcq_results=mcq_results,
        coding_results=coding_results
    )