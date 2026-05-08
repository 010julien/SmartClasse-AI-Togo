# SmartClasse — Main FastAPI Application

import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

# Import agents
from src.agents.adaptix import AdaptixAgent
from src.agents.linguix import LinguixAgent
from src.config import Settings

# Load environment
load_dotenv()
settings = Settings()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartClasse",
    description="Système éducatif adaptatif souverain du Togo",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
adaptix = AdaptixAgent()
linguix = LinguixAgent()

# ============= HEALTH CHECK =============
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "0.1.0",
        "gemma4_model": "loaded" if adaptix.llm else "not_loaded"
    }

# ============= ADAPTIX ENDPOINTS =============
@app.post("/agents/adaptix/generate")
async def adaptix_generate(request: dict):
    """
    ADAPTIX: Generate personalized exercise
    
    Input:
    {
        "student_name": "Kossi",
        "level": "CM1",
        "subject": "math",
        "topic": "fractions",
        "language": "kabyie"
    }
    """
    try:
        exercise = adaptix.generate_exercise(
            student_name=request.get("student_name"),
            level=request.get("level"),
            subject=request.get("subject"),
            topic=request.get("topic"),
            language=request.get("language", "french")
        )
        return {"status": "success", "exercise": exercise}
    except Exception as e:
        logger.error(f"ADAPTIX error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/adaptix/evaluate")
async def adaptix_evaluate(request: dict):
    """
    ADAPTIX: Evaluate student response and update profile
    
    Input:
    {
        "student_id": "kossi_001",
        "exercise_id": "ex_123",
        "response": "4/8",
        "is_correct": true
    }
    """
    try:
        result = adaptix.evaluate_response(
            student_id=request.get("student_id"),
            exercise_id=request.get("exercise_id"),
            response=request.get("response"),
            is_correct=request.get("is_correct")
        )
        return {"status": "success", "update": result}
    except Exception as e:
        logger.error(f"ADAPTIX evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= LINGUIX ENDPOINTS =============
@app.post("/agents/linguix/transcribe")
async def linguix_transcribe(file: UploadFile = File(...)):
    """
    LINGUIX: Transcribe audio to text (Whisper)
    Supports: Kabyie, Ewe, Haoussa, Mina, Tem, French
    """
    try:
        # Save uploaded file temporarily
        audio_path = f"/tmp/{file.filename}"
        with open(audio_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe using Whisper
        transcription = linguix.transcribe(audio_path)
        
        # Cleanup
        os.remove(audio_path)
        
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        logger.error(f"LINGUIX transcribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/linguix/translate_instruction")
async def linguix_translate(request: dict):
    """
    LINGUIX: Translate instruction to multiple local languages
    
    Input:
    {
        "instruction": "Calculez le quart de 48",
        "source_language": "french",
        "target_languages": ["kabyie", "ewe", "haoussa"],
        "audio_output": true
    }
    """
    try:
        translations = linguix.translate_instruction(
            instruction=request.get("instruction"),
            source_language=request.get("source_language", "french"),
            target_languages=request.get("target_languages", ["kabyie"]),
            audio_output=request.get("audio_output", False)
        )
        return {"status": "success", "translations": translations}
    except Exception as e:
        logger.error(f"LINGUIX translate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= FUTURE ENDPOINTS (Phase 2+) =============
@app.post("/agents/diagnostix/analyze")
async def diagnostix_analyze(request: dict):
    """DIAGNOSTIX: Detect precise skill gaps"""
    return {"status": "coming_soon", "agent": "diagnostix"}

@app.get("/agents/pilotix/dashboard")
async def pilotix_dashboard(teacher_id: str):
    """PILOTIX: Teacher dashboard with real-time class data"""
    return {"status": "coming_soon", "agent": "pilotix"}

@app.post("/agents/equitix/risk_assessment")
async def equitix_assess(student_id: str):
    """EQUITIX: Detect dropout risk for girls"""
    return {"status": "coming_soon", "agent": "equitix"}

@app.post("/agents/parentix/send_sms")
async def parentix_send(request: dict):
    """PARENTIX: Send weekly SMS to parent in local language"""
    return {"status": "coming_soon", "agent": "parentix"}

# ============= ROOT =============
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "project": "SmartClasse",
        "description": "Système éducatif adaptatif souverain du Togo",
        "version": "0.1.0",
        "hackathon": "Kaggle Gemma 4 Good",
        "endpoints": {
            "health": "/health",
            "adaptix": "/agents/adaptix/generate",
            "linguix": "/agents/linguix/transcribe",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
