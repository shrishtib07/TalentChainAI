# ai_engine/llm_utils.py

import os
import json # Import the json library
from openai import OpenAI
from .prompts import (
    ASSESSMENT_GENERATOR_SYSTEM_PROMPT, 
    get_assessment_prompt,
    EVALUATOR_SYSTEM_PROMPT,  
    get_evaluation_prompt,   
    RESUME_ANALYZER_SYSTEM_PROMPT,  
    get_resume_analysis_prompt    
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

# --- This is your existing function (NOW FIXED) ---
def generate_assessment_question(job_role: str) -> str:  # <-- REMOVED ASYNC
    """
    Calls the Groq API to generate a unique assessment question.
    """
    if not client:
        return "Error: Groq client not initialized."
    try:
        completion = client.chat.completions.create(  # <-- REMOVED AWAIT
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
# --- THIS FUNCTION FOR THE EVALUATOR (NOW FIXED) ---
# --- --------------------------------------------------- ---
def evaluate_candidate_answer(question: str, answer: str, skill: str) -> dict: # <-- REMOVED ASYNC
    """
    Calls the Groq API to evaluate a candidate's answer and return JSON.
    """
    if not client:
        return {"error": "Groq client not initialized."}

    try:
        completion = client.chat.completions.create( # <-- REMOVED AWAIT
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
    
def analyze_resume_text(resume_text: str) -> dict:
    """
    Calls the Groq API to analyze resume text and extract skills.
    """
    if not client:
        return {"error": "Groq client not initialized."}
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}, 
            messages=[
                {"role": "system", "content": RESUME_ANALYZER_SYSTEM_PROMPT},
                {"role": "user", "content": get_resume_analysis_prompt(resume_text)}
            ],
            temperature=0.0 # We want a factual, deterministic extraction
        )
        
        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        print(f"Error calling Groq API (resume): {e}")
        return {"error": "Could not analyze resume."}