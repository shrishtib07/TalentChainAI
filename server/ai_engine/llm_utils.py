# ai_engine/llm_utils.py

import os
import json # Import the json library
from openai import OpenAI
from .prompts import (
    ASSESSMENT_GENERATOR_SYSTEM_PROMPT, 
    get_assessment_prompt,
    EVALUATOR_SYSTEM_PROMPT,  # <-- Import new prompt
    get_evaluation_prompt   # <-- Import new prompt
)

# Your existing client initialization (connects to Groq)
try:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )
    client.models.list() 
    print("Groq client initialized successfully.")
except Exception as e:
    print(f"Error initializing Groq/OpenAI client: {e}")
    client = None

# --- This is your existing function ---
async def generate_assessment_question(job_role: str) -> str:
    if not client:
        return "Error: Groq client not initialized."
    try:
        completion = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": ASSESSMENT_GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": get_assessment_prompt(job_role)}
            ],
            temperature=0.7,
            max_tokens=250
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling Groq API (generate): {e}")
        return "Error: Could not generate question from AI."


# --- --------------------------------------------------- ---
# --- ADD THIS NEW FUNCTION FOR THE EVALUATOR ---
# --- --------------------------------------------------- ---

async def evaluate_candidate_answer(question: str, answer: str, skill: str) -> dict:
    """
    Calls the Groq API to evaluate a candidate's answer and return JSON.
    """
    if not client:
        return {"error": "Groq client not initialized."}

    try:
        completion = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            # This is a powerful feature that FORCES the LLM to output valid JSON
            response_format={"type": "json_object"}, 
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": get_evaluation_prompt(question, answer, skill)}
            ],
            temperature=0.2 # Lower temp for more deterministic, factual evaluation
        )
        
        # Parse the JSON string from the LLM into a Python dictionary
        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        print(f"Error calling Groq API (evaluate): {e}")
        return {"error": "Could not evaluate answer."}