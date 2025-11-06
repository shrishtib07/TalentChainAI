from dotenv import load_dotenv
import os

# --- THIS MUST BE THE FIRST THING THAT RUNS ---
load_dotenv()
# --- --------------------------------------- ---

from fastapi import FastAPI
from routes import assessment #, resume
from fastapi.middleware.cors import CORSMiddleware  # <-- IMPORT THIS

app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

# --- --------------------------------------- ---
# --- ADD THIS BLOCK TO ENABLE CORS ---
# --- --------------------------------------- ---
# This allows your frontend (running on a different port)
# to make requests to your backend.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For testing, allow ALL origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- --------------------------------------- ---


# --- Include Routers ---
app.include_router(assessment.router)
# app.include_router(resume.router) # Uncomment this if you added it

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}