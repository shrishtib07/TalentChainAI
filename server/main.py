from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from routes import assessment, resume
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

# This is our simple in-memory "database"
app.state.test_cache = {} 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UPDATED LINE ---
# This passes the 'app.state' to the router functions
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Assessment"])
# This router doesn't need the cache, so it's fine
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}