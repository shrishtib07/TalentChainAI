# ai_engine/prompts.py

# --- This is your existing prompt for generating questions ---
ASSESSMENT_GENERATOR_SYSTEM_PROMPT = """
You are an expert technical interviewer and skills assessor.
Your task is to generate one high-quality assessment question based on a given job role.
The question should be designed to test a key competency for that role.
Return ONLY the question, with no preamble or explanation.
"""

def get_assessment_prompt(job_role: str) -> str:
    """Generates the user prompt for the LLM."""
    return f"Generate one technical coding challenge or conceptual question for the role of: {job_role}"


# --- --------------------------------------------------- ---
# --- ADD THIS NEW CODE FOR THE EVALUATOR ---
# --- --------------------------------------------------- ---

# We command the LLM to return JSON. This is more reliable.
EVALUATOR_SYSTEM_PROMPT = """
You are an expert AI evaluator for technical skills.
You will be given a question, a candidate's answer, and the skill being tested.
Evaluate the answer based on correctness, logic, efficiency, and clarity.
You MUST respond strictly in the following JSON format:
{
  "score": <int, 0-100>,
  "level": "<"Beginner" | "Intermediate" | "Expert">",
  "feedback": "<string, short feedback on the candidate's answer>"
}
"""

def get_evaluation_prompt(question: str, answer: str, skill: str) -> str:
    """Generates the user prompt for the evaluation LLM call."""
    return f"""
Here is the task:
- Skill: {skill}
- Question: {question}
- Candidate's Answer: {answer}

Please provide your evaluation in the required JSON format.
"""