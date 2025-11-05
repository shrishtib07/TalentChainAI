ASSESSMENT_GENERATOR_SYSTEM_PROMPT = """
You are an expert technical interviewer and skills assessor.
Your task is to generate one high-quality assessment question based on a given job role.
The question should be designed to test a key competency for that role.
Return ONLY the question, with no preamble or explanation.
"""

def get_assessment_prompt(job_role: str) -> str:
    """Generates the user prompt for the LLM."""
    return f"Generate one technical coding challenge or conceptual question for the role of: {job_role}"