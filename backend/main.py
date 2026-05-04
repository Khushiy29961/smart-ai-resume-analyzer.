from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel
import json
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume & Skill Gap Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for initial deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

# Initialize Vertex AI
# Project and location should ideally be passed via env vars, but if omitted, ADC picks up defaults.
try:
    vertexai.init(location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")

@app.post("/analyze")
async def analyze_resume(request: AnalysisRequest):
    if not request.resume_text or not request.job_description:
        raise HTTPException(status_code=400, detail="Both resume_text and job_description are required.")

    prompt = f"""
    You are an expert Senior Cloud Architect, AI Engineer, and a modern AI-driven Applicant Tracking System (ATS).
    Your task is to analyze the following resume against the provided job description and bridge the 'Semantic Gap'.
    This means you must understand implied skills from project descriptions, academic work, and extracurriculars, and align them with the industry keywords found in the Job Description.

    Job Description:
    {request.job_description}

    Resume:
    {request.resume_text}

    Provide your analysis as a structured JSON object with the following keys exactly:
    - "match_score": A contextual percentage (0-100) integer. Weigh exact technical skills heavily (40%), inferred technical skills from projects/experience (30%), soft skills (20%), and experience level (10%).
    - "skill_gaps": A list of strings identifying missing technical and soft skills.
    - "impact_rewrites": A list of 3 strings. Each should be an actionable, quantifiable bullet point suggestion to optimize the resume for an ATS, based on their existing experience.
    - "learning_roadmap": A list of 3 strings. Each should be a specific learning topic or search query relevant to GeeksforGeeks to address the identified skill gaps.

    Return ONLY valid JSON. Do not use Markdown formatting like ```json or anything else. Just the raw JSON object.
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up possible markdown wrappers
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        result_json = json.loads(response_text)
        return result_json
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to parse the AI analysis result.")
    except Exception as e:
        logger.error(f"Error during Vertex AI generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
