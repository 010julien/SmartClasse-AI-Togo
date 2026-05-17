# SmartClasse — Main FastAPI Application

import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.adaptix import AdaptixAgent
from src.agents.diagnostix import DiagnostixAgent
from src.agents.equitix import EquitixAgent
from src.agents.kulturix import KulturixAgent
from src.agents.parentix import ParentixAgent
from src.agents.pilotix import PilotixAgent
from src.agents.linguix import LinguixAgent
from src.config import settings
from src.db import init_db, load_student_profile
from src.agents.orchestrator import OrchestratorAgent


load_dotenv()

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

if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
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


# ---------------------------------------------------------------------------
# Request models — validation Pydantic sur tous les endpoints POST
# ---------------------------------------------------------------------------

class OrchestratorGenerateRequest(BaseModel):
    student_id: Optional[str] = None
    student_name: str = "Student"
    level: str = "CE1"
    subject: str = "math"
    topic: str = "fractions"
    language: str = "french"


class AdaptixGenerateRequest(BaseModel):
    student_name: str
    level: str
    subject: str
    topic: str
    language: str = "french"


class AdaptixDiagnosticRequest(BaseModel):
    student_name: str = "Kossi"
    level: str = "CE1"
    language: str = "french"


class AdaptixProfileRequest(BaseModel):
    student_id: str
    responses: List[Any] = []


class AdaptixEvaluateRequest(BaseModel):
    student_id: str
    exercise_id: str
    response: Any = None
    is_correct: bool = False


class LinguixTranslateRequest(BaseModel):
    instruction: str
    source_language: str = "french"
    target_languages: List[str] = ["kabyie"]
    audio_output: bool = False


class LinguixTtsRequest(BaseModel):
    text: str
    language: str = "french"


class DiagnostixAnalyzeRequest(BaseModel):
    student_id: str
    student_name: str
    level: str
    language: str = "french"


class PilotixDashboardRequest(BaseModel):
    teacher_name: str = "Enseignant"
    class_name: str = "Classe A"
    student_ids: List[str] = []
    language: str = "french"


class EquitixRiskRequest(BaseModel):
    student_id: str
    student_name: str
    language: str = "french"
    signals: Dict[str, Any] = {}


class ParentixSmsRequest(BaseModel):
    student_id: str
    phone_number: str
    student_name: str
    language: str = "french"
    dry_run: bool = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

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
async def orchestrator_generate(request: OrchestratorGenerateRequest):
    try:
        exercise = await run_in_threadpool(
            orchestrator.generate_personalized_exercise,
            request.student_id,
            request.student_name,
            request.level,
            request.subject,
            request.topic,
            request.language,
        )
        return {"status": "success", "exercise": exercise}
    except Exception as e:
        logger.error("ORCHESTRATOR error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne ORCHESTRATOR")


@app.post("/agents/adaptix/generate")
async def adaptix_generate(request: AdaptixGenerateRequest):
    try:
        exercise = await run_in_threadpool(
            adaptix.generate_exercise,
            request.student_name,
            request.level,
            request.subject,
            request.topic,
            request.language,
        )
        return {"status": "success", "exercise": exercise}
    except Exception as e:
        logger.error("ADAPTIX error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne ADAPTIX")


@app.post("/agents/adaptix/diagnostic")
async def adaptix_diagnostic(request: AdaptixDiagnosticRequest):
    try:
        exercises = await run_in_threadpool(
            adaptix.generate_diagnostic_exercises,
            request.student_name,
            request.level,
            request.language,
        )
        return {"status": "success", "diagnostic_exercises": exercises}
    except Exception as e:
        logger.error("ADAPTIX diagnostic error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne ADAPTIX diagnostic")


@app.post("/agents/adaptix/profile")
async def adaptix_profile(request: AdaptixProfileRequest):
    try:
        profile = await run_in_threadpool(
            adaptix.build_student_profile,
            request.student_id,
            request.responses,
        )
        return {"status": "success", "profile": profile}
    except Exception as e:
        logger.error("ADAPTIX profile error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne ADAPTIX profile")


@app.get("/agents/adaptix/profile/{student_id}")
async def adaptix_get_profile(student_id: str):
    profile = load_student_profile(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return {"status": "success", "profile": profile}


@app.post("/agents/adaptix/evaluate")
async def adaptix_evaluate(request: AdaptixEvaluateRequest):
    try:
        result = await run_in_threadpool(
            adaptix.evaluate_response,
            request.student_id,
            request.exercise_id,
            request.response,
            request.is_correct,
        )
        return {"status": "success", "update": result}
    except Exception as e:
        logger.error("ADAPTIX evaluation error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne ADAPTIX evaluate")


@app.post("/agents/linguix/transcribe")
async def linguix_transcribe(file: UploadFile = File(...), language_hint: str = Form(default="")):
    audio_path: Optional[str] = None
    try:
        suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            audio_path = tmp.name

        transcription = await run_in_threadpool(
            linguix.transcribe,
            audio_path,
            language_hint or None,
        )
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        logger.error("LINGUIX transcribe error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne LINGUIX transcribe")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


@app.post("/agents/linguix/chat")
async def linguix_chat(
    request: Request,
    file: UploadFile = File(None),
    language: str = Form(default=None),
    speak: bool = Form(default=None),
    user_level: str = Form(default=None),
    user_id: str = Form(default=None),
    user_name: str = Form(default=None),
):
    """Chat endpoint — accepte multipart/form-data (audio) ou JSON."""
    audio_path: Optional[str] = None
    try:
        if file is not None:
            suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await file.read())
                audio_path = tmp.name

            lang = language or "french"
            speak_flag = bool(speak) if speak is not None else True
            result = await run_in_threadpool(
                linguix.chat_voice,
                None,
                audio_path,
                lang,
                user_id,
                user_name,
                speak_flag,
            )
            return {"status": "success", "result": result}

        body = await request.json()
        messages_payload = body.get("messages") or []
        speak_flag = bool(body.get("speak", False))
        language = body.get("language", "french")
        user_level = body.get("user_level", "CE1")
        user_id = body.get("user_id")
        user_name = body.get("user_name", "Student")

        result = await run_in_threadpool(
            linguix.chat,
            messages_payload,
            speak_flag,
            language,
            user_level,
            user_id,
            user_name,
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("LINGUIX chat error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne LINGUIX chat")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


class LinguixStreamRequest(BaseModel):
    messages: List[Dict[str, Any]] = []
    language: str = "french"
    user_level: str = "CE1"
    session_id: Optional[str] = None
    user_name: str = "Student"


# Instance partagée du pipeline avancé (réutilise la même mémoire)
from src.advanced.nlu_engine import NLUEngine
from src.advanced.memory_manager import MemoryManager
from src.advanced.prompts import AdvancedPromptEngineering

_stream_nlu = NLUEngine()
_stream_memory = MemoryManager()
_stream_prompts = AdvancedPromptEngineering()


@app.post("/agents/linguix/chat/stream")
async def linguix_chat_stream(request: LinguixStreamRequest):
    """Streaming chat endpoint avec pipeline avancé intégré.

    Exécute NLU + Memory + PromptEngineering AVANT le streaming,
    puis stream les tokens SSE depuis Ollama,
    puis met à jour la mémoire APRÈS le stream.
    """
    import json as _json
    import uuid

    try:
        import ollama as _ollama
    except ImportError:
        raise HTTPException(status_code=500, detail="Ollama non disponible")

    # ── Phase 1 : Extraire le dernier message utilisateur ────────────────
    last_user_message = ""
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            last_user_message = (msg.get("content") or "").strip()
            break

    if not last_user_message:
        raise HTTPException(status_code=400, detail="Aucun message utilisateur")

    # ── Phase 2 : Session et mémoire ─────────────────────────────────────
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{session_id[-8:]}"
    user_name = request.user_name if request.user_name != "Student" else "Élève"

    session_init = _stream_memory.initialize_session(session_id, user_id, user_name)
    user_profile = session_init["user_profile"]

    # Récupérer le contexte mémoire (tours précédents de cette session)
    memory_context = _stream_memory.get_context_for_response(session_id, user_id)
    user_context = memory_context.get("user", {})
    user_context.update({
        "user_name": user_name,
        "educational_level": request.user_level,
        "preferred_language": request.language,
    })

    logger.info(
        f"STREAM | Session: {session_id} | User: {user_name} | "
        f"Level: {request.user_level} | History: {len(request.messages)} msgs | "
        f"Message: {last_user_message[:50]}..."
    )

    # ── Phase 3 : NLU — classification d'intent ─────────────────────────
    nlu_result = _stream_nlu.analyze(last_user_message, request.messages)
    intent = nlu_result["intent"]

    logger.info(f"STREAM NLU | Intent: {intent.type.value} (conf: {nlu_result['analysis_confidence']:.2f})")

    # ── Phase 4 : Prompt Engineering sophistiqué ─────────────────────────
    system_prompt = _stream_prompts.build_system_prompt(
        intent, user_context, memory_context.get("conversation")
    )
    user_message_with_context = _stream_prompts.build_user_message_with_context(
        last_user_message,
        intent,
        user_context,
        memory_context.get("conversation_summary"),
    )

    # ── Phase 5 : Construire les messages LLM ────────────────────────────
    llm_messages = [
        {"role": "system", "content": system_prompt},
    ]
    # Inclure l'historique conversationnel (sans le dernier message user, qui est enrichi)
    for msg in request.messages[:-1]:
        if msg.get("role") in ("user", "assistant"):
            llm_messages.append({"role": msg["role"], "content": msg.get("content", "")})
    # Ajouter le message utilisateur enrichi
    llm_messages.append({"role": "user", "content": user_message_with_context})

    logger.info(f"STREAM | LLM messages: {len(llm_messages)} | System prompt: {len(system_prompt)} chars")

    # ── Phase 6 : Streaming SSE ──────────────────────────────────────────
    async def event_generator():
        full_response = []
        try:
            client = _ollama.Client(
                host=settings.OLLAMA_BASE_URL,
                timeout=settings.OLLAMA_TIMEOUT,
            )
            stream = client.chat(
                model=settings.LLM_MODEL,
                messages=llm_messages,
                stream=True,
                options={
                    "temperature": settings.LLM_TEMPERATURE,
                    "num_predict": settings.LLM_MAX_TOKENS,
                    "num_ctx": settings.LLM_CONTEXT_WINDOW,
                },
            )
            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                if token:
                    full_response.append(token)
                    data = _json.dumps({"token": token}, ensure_ascii=False)
                    yield f"data: {data}\n\n"

            # ── Phase 7 : Mise à jour mémoire après streaming ────────────
            assistant_text = "".join(full_response)
            if assistant_text:
                _stream_memory.add_turn(session_id, user_id, last_user_message, assistant_text)
                logger.info(f"STREAM | Memory updated | Session: {session_id} | Response: {len(assistant_text)} chars")

            # Signal de fin
            yield f"data: {_json.dumps({'done': True})}\n\n"
        except Exception as exc:
            logger.error("Stream error: %s", exc, exc_info=True)
            yield f"data: {_json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/agents/linguix/translate_instruction")
async def linguix_translate(request: LinguixTranslateRequest):
    try:
        translations = await run_in_threadpool(
            linguix.translate_instruction,
            request.instruction,
            request.source_language,
            request.target_languages,
            request.audio_output,
        )
        return {"status": "success", "translations": translations}
    except Exception as e:
        logger.error("LINGUIX translate error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne LINGUIX translate")


@app.post("/agents/linguix/voice_pipeline")
async def linguix_voice_pipeline(
    file: UploadFile = File(...),
    source_language_hint: str = Form(default="french"),
    target_languages: str = Form(default="ewe"),
):
    audio_path: Optional[str] = None
    try:
        suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            audio_path = tmp.name

        targets = [lang.strip() for lang in target_languages.split(",") if lang.strip()]
        pipeline = await run_in_threadpool(
            linguix.voice_pipeline,
            audio_path,
            targets or ["ewe"],
            source_language_hint or None,
        )
        return {"status": "success", "pipeline": pipeline}
    except Exception as e:
        logger.error("LINGUIX voice pipeline error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne LINGUIX voice pipeline")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


@app.post("/agents/linguix/tts_stream")
async def linguix_tts_stream(request: LinguixTtsRequest):
    """Stream TTS audio. Corps: { "text": "...", "language": "french" }"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide")
    try:
        gen = linguix.tts.synthesize_stream(request.text)
        return StreamingResponse(gen, media_type="audio/wav")
    except Exception as e:
        logger.error("LINGUIX tts_stream error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne LINGUIX TTS")


@app.post("/agents/diagnostix/analyze")
async def diagnostix_analyze(request: DiagnostixAnalyzeRequest):
    try:
        result = await run_in_threadpool(
            diagnostix.analyze_student,
            request.student_id,
            request.student_name,
            request.level,
            request.language,
        )
        return {"status": "success", "analysis": result}
    except Exception as e:
        logger.error("DIAGNOSTIX analyze error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne DIAGNOSTIX")


@app.post("/agents/pilotix/dashboard")
async def pilotix_dashboard(request: PilotixDashboardRequest):
    try:
        dashboard = await run_in_threadpool(
            pilotix.build_dashboard,
            request.teacher_name,
            request.class_name,
            request.student_ids,
            request.language,
        )
        return {"status": "success", "dashboard": dashboard}
    except Exception as e:
        logger.error("PILOTIX dashboard error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne PILOTIX")


@app.post("/agents/equitix/risk_assessment")
async def equitix_assess(request: EquitixRiskRequest):
    try:
        result = await run_in_threadpool(
            equitix.assess_dropout_risk,
            request.student_id,
            request.student_name,
            request.language,
            request.signals,
        )
        return {"status": "success", "assessment": result}
    except Exception as e:
        logger.error("EQUITIX assessment error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne EQUITIX")


@app.post("/agents/parentix/send_sms")
async def parentix_send(request: ParentixSmsRequest):
    try:
        result = await run_in_threadpool(
            parentix.send_weekly_message,
            request.student_id,
            request.phone_number,
            request.student_name,
            request.language,
            request.dry_run,
        )
        return {"status": "success", "sms": result}
    except Exception as e:
        logger.error("PARENTIX sms error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne PARENTIX")


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
