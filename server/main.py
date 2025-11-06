from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
# Load .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI
app = FastAPI(title="TalentChain AI Skill Verifier")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input models
class UserAnswer(BaseModel):
    question: str
    answer: str
    skill: str

class AssessmentRequest(BaseModel):
    role: str

class QuestionRequest(BaseModel):
    skill: str
    count: int = 3

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "TalentChain AI API is running", "version": "1.0.0"}

# Route to generate assessment question for a role
@app.post("/api/v1/assessment/generate")
def generate_assessment(request: AssessmentRequest):
    prompt = f"""
    Generate one high-quality technical assessment question for the role of: {request.role}
    The question should test a key competency for this role.
    Return ONLY the question, with no preamble or explanation.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer and skills assessor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        question = response.choices[0].message.content.strip()
        return {"question": question, "role": request.role}
    
    except Exception as e:
        return {"error": str(e), "question": "Error generating question"}

# Route to evaluate a user's answer
@app.post("/api/v1/evaluate")
def evaluate_skill(data: UserAnswer):
    prompt = f"""
    You are an expert evaluator for {data.skill}.
    Evaluate the following answer based on correctness, logic, and clarity.
    Give a score (0-100), a skill level (Beginner / Intermediate / Expert),
    and short feedback.

    Question: {data.question}
    Candidate Answer: {data.answer}

    Respond strictly in JSON format like:
    {{
      "score": 85,
      "level": "Intermediate",
      "feedback": "Good approach, minor syntax issues."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI skill evaluator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            parsed_result = json.loads(result)
            return parsed_result
        except:
            # If not valid JSON, return as text
            return {"score": 0, "level": "Unknown", "feedback": result}
    
    except Exception as e:
        return {"score": 0, "level": "Error", "feedback": f"Error evaluating answer: {str(e)}"}

# Route to generate multiple sample questions dynamically
@app.post("/api/v1/generate-questions")
def generate_questions(request: QuestionRequest):
    prompt = f"""
    Generate {request.count} coding or logic questions to test {request.skill} skill.
    Return only a JSON array of questions in this format:
    [
      {{"id": 1, "question": "Question text here"}},
      {{"id": 2, "question": "Question text here"}},
      ...
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional question generator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        result = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            questions = json.loads(result)
            return {"questions": questions, "skill": request.skill}
        except:
            return {"questions": [], "error": "Failed to parse questions"}
    
    except Exception as e:
        return {"questions": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)