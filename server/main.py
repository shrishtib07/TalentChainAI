# main.py

from dotenv import load_dotenv
import os

# --- THIS MUST BE THE FIRST THING THAT RUNS ---
# Load all environment variables from the .env file
# BEFORE any other modules are imported
load_dotenv()
# --- --------------------------------------- ---

from fastapi import FastAPI
from routes import assessment  # <-- Now this import will work
# (add 'resume' router here later if you've added it)
# from routes import assessment, resume

# Create the main FastAPI application
app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

# --- Include Routers ---
app.include_router(assessment.router)
# app.include_router(resume.router)

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}