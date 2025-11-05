# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI
app = FastAPI(title="TalentChain AI Skill Verifier")

# Define input model
class UserAnswer(BaseModel):
    question: str
    answer: str
    skill: str

# Route to evaluate a user's answer
@app.post("/evaluate")
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI skill evaluator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Route to generate sample questions dynamically
@app.get("/generate/{skill}")
def generate_questions(skill: str):
    prompt = f"""
    Generate 3 coding or logic questions to test {skill} skill.
    Return only a JSON list of questions.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional question generator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
