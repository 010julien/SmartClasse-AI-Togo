# SmartClasse — Main FastAPI Application

import logging
import os
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.agents.adaptix import AdaptixAgent
from src.agents.diagnostix import DiagnostixAgent
from src.agents.equitix import EquitixAgent
from src.agents.kulturix import KulturixAgent
from src.agents.parentix import ParentixAgent
from src.agents.pilotix import PilotixAgent
from src.agents.linguix import LinguixAgent
from src.config import Settings
from src.db import init_db, load_student_profile
from src.agents.orchestrator import OrchestratorAgent


load_dotenv()
settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()

app = FastAPI(
    title="SmartClasse",
    description="Système éducatif adaptatif souverain du Togo",
    version="0.1.0",
)

os.makedirs(os.path.join("data", "audio"), exist_ok=True)
app.mount("/audio", StaticFiles(directory=os.path.join("data", "audio")), name="audio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adaptix = AdaptixAgent()
diagnostix = DiagnostixAgent()
pilotix = PilotixAgent()
equitix = EquitixAgent()
parentix = ParentixAgent()
linguix = LinguixAgent()
kulturix = KulturixAgent()
orchestrator = OrchestratorAgent(adaptix, linguix, kulturix, diagnostix, equitix, pilotix, parentix)


@app.get("/health")
async def health():
    return {
        "status": "online",
        "version": "0.1.0",
        "gemma4_model": settings.LLM_MODEL,
        "database": settings.DATABASE_URL,
    }


@app.get("/agents/kulturix/context")
async def kulturix_context(query: str = "sorgho karité marché famille"):
    return {
        "status": "success",
        "context": kulturix.get_context_pack(query),
    }


@app.post("/agents/orchestrator/generate")
async def orchestrator_generate(request: dict):
    try:
        exercise = await run_in_threadpool(
            orchestrator.generate_personalized_exercise,
            request.get("student_id"),
            request.get("student_name", "Student"),
            request.get("level", "CE1"),
            request.get("subject", "math"),
            request.get("topic", "fractions"),
            request.get("language", "french"),
        )
        return {"status": "success", "exercise": exercise}
    except Exception as e:
        logger.error(f"ORCHESTRATOR error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/adaptix/generate")
async def adaptix_generate(request: dict):
    try:
        exercise = await run_in_threadpool(
            adaptix.generate_exercise,
            request.get("student_name"),
            request.get("level"),
            request.get("subject"),
            request.get("topic"),
            request.get("language", "french"),
        )
        return {"status": "success", "exercise": exercise}
    except Exception as e:
        logger.error(f"ADAPTIX error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/adaptix/diagnostic")
async def adaptix_diagnostic(request: dict):
    try:
        exercises = await run_in_threadpool(
            adaptix.generate_diagnostic_exercises,
            request.get("student_name", "Kossi"),
            request.get("level", "CE1"),
            request.get("language", "french"),
        )
        return {"status": "success", "diagnostic_exercises": exercises}
    except Exception as e:
        logger.error(f"ADAPTIX diagnostic error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/adaptix/profile")
async def adaptix_profile(request: dict):
    try:
        profile = await run_in_threadpool(
            adaptix.build_student_profile,
            request.get("student_id"),
            request.get("responses", []),
        )
        return {"status": "success", "profile": profile}
    except Exception as e:
        logger.error(f"ADAPTIX profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/adaptix/profile/{student_id}")
async def adaptix_get_profile(student_id: str):
    profile = load_student_profile(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"status": "success", "profile": profile}


@app.post("/agents/adaptix/evaluate")
async def adaptix_evaluate(request: dict):
    try:
        result = await run_in_threadpool(
            adaptix.evaluate_response,
            request.get("student_id"),
            request.get("exercise_id"),
            request.get("response"),
            request.get("is_correct"),
        )
        return {"status": "success", "update": result}
    except Exception as e:
        logger.error(f"ADAPTIX evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/linguix/transcribe")
async def linguix_transcribe(file: UploadFile = File(...), language_hint: str = Form(default="")):
    try:
        suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            audio_path = temp_file.name

        transcription = await run_in_threadpool(
            linguix.transcribe,
            audio_path,
            language_hint or None,
        )

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {"status": "success", "transcription": transcription}
    except Exception as e:
        logger.error(f"LINGUIX transcribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/linguix/chat")
async def linguix_chat(request: dict):
    """Proxy chat endpoint to LINGUIX Premium: Natural, contextual, reasoning-powered conversations.

    Body JSON: {
        "messages": [{"role":"user","content":"..."}, ...],
        "speak": true/false,
        "language": "french" (or kabyie, ewe, haoussa, mina, tem),
        "user_level": "CE1" (or CE2, CM1, CM2, 6e, etc.),
        "user_id": "student_123" (optional, for personalization),
        "user_name": "Kossi" (optional, for personalization)
    }
    """
    try:
        messages = request.get("messages") or []
        speak = bool(request.get("speak", False))
        language = request.get("language", "french")
        user_level = request.get("user_level", "CE1")
        user_id = request.get("user_id")
        user_name = request.get("user_name", "Student")

        result = await run_in_threadpool(
            linguix.chat,
            messages,
            speak,
            language,
            user_level,
            user_id,
            user_name,
        )

        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"LINGUIX chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/linguix/translate_instruction")
async def linguix_translate(request: dict):
    try:
        translations = await run_in_threadpool(
            linguix.translate_instruction,
            request.get("instruction"),
            request.get("source_language", "french"),
            request.get("target_languages", ["kabyie"]),
            request.get("audio_output", False),
        )
        return {"status": "success", "translations": translations}
    except Exception as e:
        logger.error(f"LINGUIX translate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/linguix/voice_pipeline")
async def linguix_voice_pipeline(
    file: UploadFile = File(...),
    source_language_hint: str = Form(default="french"),
    target_languages: str = Form(default="ewe"),
):
    try:
        suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            audio_path = temp_file.name

        targets = [language.strip() for language in target_languages.split(",") if language.strip()]
        pipeline = await run_in_threadpool(
            linguix.voice_pipeline,
            audio_path,
            targets or ["ewe"],
            source_language_hint or None,
        )

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {"status": "success", "pipeline": pipeline}
    except Exception as e:
        logger.error(f"LINGUIX voice pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/diagnostix/analyze")
async def diagnostix_analyze(request: dict):
    try:
        result = await run_in_threadpool(
            diagnostix.analyze_student,
            request.get("student_id"),
            request.get("student_name"),
            request.get("level"),
            request.get("language", "french"),
        )
        return {"status": "success", "analysis": result}
    except Exception as e:
        logger.error(f"DIAGNOSTIX analyze error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/pilotix/dashboard")
async def pilotix_dashboard(request: dict):
    try:
        dashboard = await run_in_threadpool(
            pilotix.build_dashboard,
            request.get("teacher_name", "Enseignant"),
            request.get("class_name", "Classe A"),
            request.get("student_ids", []),
            request.get("language", "french"),
        )
        return {"status": "success", "dashboard": dashboard}
    except Exception as e:
        logger.error(f"PILOTIX dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/equitix/risk_assessment")
async def equitix_assess(request: dict):
    try:
        result = await run_in_threadpool(
            equitix.assess_dropout_risk,
            request.get("student_id"),
            request.get("student_name"),
            request.get("language", "french"),
            request.get("signals", {}),
        )
        return {"status": "success", "assessment": result}
    except Exception as e:
        logger.error(f"EQUITIX assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/parentix/send_sms")
async def parentix_send(request: dict):
    try:
        result = await run_in_threadpool(
            parentix.send_weekly_message,
            request.get("student_id"),
            request.get("phone_number"),
            request.get("student_name"),
            request.get("language", "french"),
            request.get("dry_run", True),
        )
        return {"status": "success", "sms": result}
    except Exception as e:
        logger.error(f"PARENTIX sms error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "project": "SmartClasse",
        "description": "Système éducatif adaptatif souverain du Togo",
        "version": "0.1.0",
        "hackathon": "Kaggle Gemma 4 Good",
        "endpoints": {
            "health": "/health",
            "adaptix": "/agents/adaptix/generate",
            "diagnostic": "/agents/adaptix/diagnostic",
            "diagnostix": "/agents/diagnostix/analyze",
            "pilotix": "/agents/pilotix/dashboard",
            "equitix": "/agents/equitix/risk_assessment",
            "parentix": "/agents/parentix/send_sms",
            "linguix": "/agents/linguix/transcribe",
            "voice_pipeline": "/agents/linguix/voice_pipeline",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
