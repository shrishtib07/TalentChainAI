import os
from openai import OpenAI
from .prompts import ASSESSMENT_GENERATOR_SYSTEM_PROMPT, get_assessment_prompt

# Initialize the OpenAI client
# It automatically reads the OPENAI_API_KEY from the .env file
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure your OPENAI_API_KEY is set in the .env file.")
    client = None

async def generate_assessment_question(job_role: str) -> str:
    """
    Calls the OpenAI API to generate a unique assessment question.
    """
    if not client:
        return "Error: OpenAI client not initialized."

    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",  # Using a fast and cost-effective model
            messages=[
                {"role": "system", "content": ASSESSMENT_GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": get_assessment_prompt(job_role)}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        question = completion.choices[0].message.content
        return question.strip()

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return "Error: Could not generate question from AI."