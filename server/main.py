# main.py
# --- THIS FILE IS ALREADY FINISHED ---

from fastapi import FastAPI
from dotenv import load_dotenv
from routes import assessment  # This now includes both /generate and /evaluate
import os

load_dotenv()

app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

app.include_router(assessment.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}
