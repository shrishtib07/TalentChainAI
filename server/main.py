from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# ✅ Load environment variables BEFORE importing routes
load_dotenv()

from routes import assessment, resume

app = FastAPI(
    title="TalentChain AI API",
    description="Backend for AI skill assessment and blockchain credentialing.",
    version="0.1.0"
)

# ✅ Temporary wide-open CORS for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assessment.router)
app.include_router(resume.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the TalentChain AI Backend!"}

