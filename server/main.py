from dotenv import load_dotenv
import os

# --- THIS MUST BE THE FIRST THING THAT RUNS ---
load_dotenv()
# --- --------------------------------------- ---

from fastapi import FastAPI
from routes import assessment, resume
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

# --- This is our simple in-memory "database" ---
app.state.test_cache = {} 

# --- ADD THIS BLOCK TO ENABLE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
# We pass 'app' to the router so it can access the cache
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Assessment"], app_state=app.state)
app.include_router(resume.router)

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}