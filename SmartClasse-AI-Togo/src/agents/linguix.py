# src/agents/linguix.py
# LINGUIX: Linguistic Bridge Agent

import hashlib
import json
import logging
import os
import shutil
import tempfile
import uuid
import numpy as np
from typing import Any, Dict, List, Optional

try:
    import imageio_ffmpeg  # type: ignore
except ImportError:
    imageio_ffmpeg = None

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None
from src.llm import call_chat
from src.prompting import build_messages, extract_json
from src.config import settings
from src.advanced.conversation_manager import ConversationManager
from src.modules.audio_input.vad import VADModule
from src.modules.audio_input.asr import ASRModule
from src.modules.audio_input.audio_normalizer import AudioNormalizer
from src.modules.context.context_hub import ContextHub
from src.modules.llm.gemma_engine import GemmaEngine
from src.modules.audio_output.tts_engine import TTSEngine
from src.modules.routing.channel_detector import ChannelDetector
from src.modules.routing.output_router import OutputRouter

try:
    import whisper  # type: ignore
except ImportError:
    whisper = None

try:
    from langdetect import DetectorFactory, detect  # type: ignore
    DetectorFactory.seed = 0
except ImportError:
    detect = None

logger = logging.getLogger(__name__)


class LinguixAgent:
    """LINGUIX: local language bridge for transcription, translation and audio."""

    SUPPORTED_LANGUAGES = {
        "kabyie": {"name": "Kabiyè", "iso639": "kab", "speakers": "200k"},
        "ewe": {"name": "Ewe", "iso639": "ee", "speakers": "500k"},
        "haoussa": {"name": "Haoussa", "iso639": "ha", "speakers": "4M"},
        "mina": {"name": "Mina", "iso639": "mna", "speakers": "50k"},
        "tem": {"name": "Tem", "iso639": "kdh", "speakers": "150k"},
        "french": {"name": "Français", "iso639": "fr", "speakers": "2M"},
    }

    def __init__(self):
        # ASR / VAD / Normalizer
        self.vad = VADModule(mode=3)
        self.asr = ASRModule(engine="openai-whisper", model_size="base", device="cpu")
        self.normalizer = AudioNormalizer(sample_rate=16000)

        # Context hub
        self.context_hub = ContextHub(session_id="global")

        # LLM & TTS
        self.gemma = GemmaEngine(model=settings.LLM_MODEL)
        self.tts = TTSEngine()
        self.channel_detector = ChannelDetector()
        self.output_router = OutputRouter()

        # Legacy/optional
        self.whisper_model = None
        self.whisper_model_name = "base"
        self.ollama_client = None
        self.gemma4_model = None
        self.language_model = None
        self.translation_memory = self._load_translation_memory()
        
        # Initialize premium conversation manager
        self.conversation_manager = ConversationManager()
        self.session_counter = 0

        logger.info("LINGUIX Agent initialized | Languages: 5 Togolese + French | Premium mode ACTIVE")

    def _ensure_whisper_model(self):
        if self.whisper_model is not None:
            return self.whisper_model

        if whisper is None:
            raise RuntimeError("Whisper n'est pas installé dans ce venv.")

        logger.info(f"LINGUIX: Loading Whisper model | Model: {self.whisper_model_name}")
        self.whisper_model = whisper.load_model(self.whisper_model_name)
        return self.whisper_model

    def _ensure_ffmpeg_available(self):
        if imageio_ffmpeg is None:
            return

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_cache_dir = os.path.join(tempfile.gettempdir(), "smartclasse_ffmpeg")
        os.makedirs(ffmpeg_cache_dir, exist_ok=True)

        ffmpeg_target = os.path.join(ffmpeg_cache_dir, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_target):
            shutil.copy2(ffmpeg_exe, ffmpeg_target)

        current_path = os.environ.get("PATH", "")
        path_parts = current_path.split(os.pathsep) if current_path else []
        if ffmpeg_cache_dir not in path_parts:
            os.environ["PATH"] = ffmpeg_cache_dir + os.pathsep + current_path if current_path else ffmpeg_cache_dir

    def _ensure_ollama_client(self):
        if ollama is None:
            return None

        if self.ollama_client is None:
            from src.config import settings

            if not settings.OLLAMA_BASE_URL:
                return None
            # Keep voice pipeline responsive with a strict model timeout.
            request_timeout = min(settings.OLLAMA_TIMEOUT, 5)
            self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL, timeout=request_timeout)

        return self.ollama_client

    def _load_translation_memory(self) -> Dict[str, Dict[str, str]]:
        """Load bilingual educational terminology for offline fallback"""
        return {
            "math_terms": {
                "fraction": {
                    "french": "fraction",
                    "kabyie": "arrad",
                    "ewe": "part-size",
                    "haoussa": "kashi",
                    "mina": "kple",
                    "tem": "kpɔ",
                },
                "multiplication": {
                    "french": "multiplication",
                    "kabyie": "timidray",
                    "ewe": "keke",
                    "haoussa": "tsara",
                    "mina": "kple",
                    "tem": "gbɔ",
                },
                "addition": {
                    "french": "addition",
                    "kabyie": "asidray",
                    "ewe": "akpakpa",
                    "haoussa": "ƙari",
                    "mina": "kple",
                    "tem": "kpɔ",
                },
                "problem": {
                    "french": "problème",
                    "kabyie": "ahalen",
                    "ewe": "se",
                    "haoussa": "matatsa",
                    "mina": "agbadza",
                    "tem": "se",
                },
            },
            "classroom_commands": {
                "read": {
                    "french": "Lisez",
                    "kabyie": "Ag-ar",
                    "ewe": "Keka",
                    "haoussa": "Karanta",
                    "mina": "Sɔ",
                    "tem": "Kpɔ",
                },
                "write": {
                    "french": "Écrivez",
                    "kabyie": "Ass",
                    "ewe": "Sɔ",
                    "haoussa": "Rubuta",
                    "mina": "Sɔ",
                    "tem": "Sɔ",
                },
                "listen": {
                    "french": "Écoutez",
                    "kabyie": "Fed",
                    "ewe": "Gbo",
                    "haoussa": "Siski",
                    "mina": "Gbo",
                    "tem": "Gbo",
                },
            },
            "cultural_context": {
                "sorghum": {
                    "french": "sorgho",
                    "kabyie": "tart",
                    "ewe": "koko",
                    "haoussa": "jero",
                    "mina": "koko",
                    "tem": "tart",
                },
                "shea": {
                    "french": "karité",
                    "kabyie": "azgzan",
                    "ewe": "karité",
                    "haoussa": "kariya",
                    "mina": "karité",
                    "tem": "azgzan",
                },
                "market": {
                    "french": "marché",
                    "kabyie": "aglam",
                    "ewe": "kasuwa",
                    "haoussa": "kasuwa",
                    "mina": "kasuwa",
                    "tem": "aglam",
                },
            },
        }

    def _safe_json_loads(self, content: str) -> Optional[Dict[str, Any]]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = text.split("\n", 1)[1]

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _translate_via_gemma4(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate via Gemma 4 with fallback."""
        prompt = f"""
You are LINGUIX, an expert in translating educational content to Togolese languages.

Translate this from {source_lang} to {target_lang}.
Keep precise for a child. Adapt vocabulary to local classroom usage.

Original ({source_lang}): "{text}"

Return ONLY the translated sentence, no commentary.
""".strip()

        try:
            messages = build_messages(
                agent_name="LINGUIX",
                role_description="Linguistic bridge for translating educational content to Togolese languages.",
                user_prompt=prompt,
                require_json=False,
            )
            response = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, retries=2)
            translated = response.get("message", {}).get("content", "").strip()
            if translated:
                return translated
        except Exception as exc:
            logger.warning(f"LINGUIX: Gemma 4 translation failed | {exc}")

        # Fallback translations
        fallback_map = {
            ("french", "kabyie"): "Xang ɔkʋ abɖɔ",
            ("french", "ewe"): "Keke ene eya enumake",
            ("french", "haoussa"): "Xin girma ɗaya",
            ("french", "tem"): "Kpɔ la gbɔ",
            ("french", "mina"): "Kple nɔvi",
        }
        return fallback_map.get((source_lang, target_lang), f"[{target_lang}] {text}")

    def transcribe(self, audio_path: str, language_hint: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file using Whisper."""
        logger.info(f"LINGUIX: Transcribing | Path: {audio_path} | Hint: {language_hint}")

        try:
            self._ensure_ffmpeg_available()
            model = self._ensure_whisper_model()

            result = model.transcribe(
                audio_path,
                language=language_hint,
                fp16=False,
            )

            text = result.get("text", "").strip()
            detected_lang = result.get("language", language_hint or "fr")

            return {
                "text": text,
                "language_detected": detected_lang,
                "language_hint": language_hint,
                "confidence": 0.90,
                "segments": result.get("segments", []),
            }
        except Exception as exc:
            logger.warning(f"LINGUIX: Transcription failed | {exc}")
            return {
                "text": "[Transcription unavailable]",
                "language_detected": language_hint or "french",
                "language_hint": language_hint,
                "confidence": 0.0,
                "status": "transcription_failed",
            }

    def translate_instruction(
        self,
        instruction: str,
        source_language: str,
        target_languages: List[str],
        audio_output: bool = True,
    ) -> List[Dict[str, Any]]:
        """Translate instruction to multiple target languages with optional audio."""
        translations = []

        for target_lang in target_languages:
            translated_text = self._translate_via_gemma4(instruction, source_language, target_lang)

            translation_entry = {
                "source_language": source_language,
                "target_language": target_lang,
                "translated_instruction": translated_text,
            }

            if audio_output:
                audio_data = self._generate_audio(translated_text, target_lang)
                translation_entry["audio"] = {
                    "audio_url": audio_data.get("audio_url"),
                    "audio_path": audio_data.get("audio_path"),
                    "duration_seconds": audio_data.get("duration_seconds"),
                }

            translations.append(translation_entry)

        return translations


    def _generate_audio(self, text: str, language: str) -> Dict[str, Any]:
        logger.info(f"LINGUIX: Generating audio | Lang: {language} | Text: {text[:50]}...")

        try:
            import pyttsx3  # type: ignore

            audio_dir = os.path.join("data", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_name = f"{language}_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}.wav"
            audio_path = os.path.join(audio_dir, audio_name)

            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            return {
                "language": language,
                "text": text,
                "audio_url": f"/audio/{audio_name}",
                "audio_path": audio_path,
                "duration_seconds": max(1.0, len(text.split()) * 0.4),
                "format": "WAV",
                "sample_rate": 16000,
                "channels": 1,
            }
        except Exception as exc:
            logger.warning(f"LINGUIX: TTS fallback used | {exc}")
            return {
                "language": language,
                "text": text,
                "audio_url": None,
                "duration_seconds": len(text.split()) * 0.4,
                "format": "WAV",
                "sample_rate": 16000,
                "channels": 1,
                "status": "tts_unavailable",
            }

    def chat(self, messages: List[Dict[str, str]], speak: bool = False, language: str = "french", user_level: str = "CE1", user_id: Optional[str] = None, user_name: str = "Student", channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Premium chat interface using advanced ConversationManager.
        
        messages: list of {"role":"user|assistant","content": "..."}
        speak: if True, generate TTS for assistant reply and return `audio_url`.
        language: preferred language (french, kabyie, ewe, haoussa, mina, tem)
        user_level: educational level (CE1, CE2, CM1, CM2, 6e, etc.)
        user_id: unique user identifier
        user_name: display name for personalization
        """
        # Generate session ID if not provided
        if not user_id:
            user_id = f"guest_{uuid.uuid4().hex[:8]}"
        if not user_name or user_name == "Student":
            user_name = f"Élève {self.session_counter % 100}"
        
        self.session_counter += 1
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        decision = self.channel_detector.detect(
            messages=messages,
            explicit_channel=channel,
            speak=speak,
            language_hint=language,
        )

        logger.info(
            f"LINGUIX Premium Chat | Session: {session_id} | User: {user_name} | Level: {user_level} | Channel: {decision.channel}"
        )

        try:
            # Use the premium conversation manager
            response = self.conversation_manager.process_conversation(
                session_id=session_id,
                user_id=user_id,
                user_name=user_name,
                messages=messages,
                language=language,
                user_level=user_level,
                max_retries_on_quality=2,  # Retry up to 2 times if quality is low
            )

            # Extract response text
            assistant_text = response.message

            logger.info(
                f"Response generated | Quality: {response.quality_score:.1f} | "
                f"Time: {response.total_time_ms:.0f}ms | Intent: {response.intent}"
            )

            # Package result
            result: Dict[str, Any] = {
                "assistant_text": assistant_text,
                "intent": response.intent,
                "confidence": response.confidence,
                "quality_score": response.quality_score,
                "reasoning_info": response.reasoning_chain,
                "session_id": session_id,
                "channel": decision.channel,
                "channel_confidence": decision.confidence,
                "channel_reason": decision.reason,
                "performance": {
                    "reasoning_time_ms": response.reasoning_time_ms,
                    "total_time_ms": response.total_time_ms,
                    "used_regeneration": response.used_regeneration,
                },
            }

            # Generate audio if requested
            routed = self.output_router.route_voice(assistant_text, result.get("audio"), {"channel": decision.channel}) if decision.channel == "voice" else self.output_router.route_text(assistant_text, {"channel": decision.channel})

            if speak or decision.audio_expected:
                audio = self._generate_audio(assistant_text, language)
                result.update({"audio_url": audio.get("audio_url"), "audio_path": audio.get("audio_path")})
                routed = self.output_router.route_voice(assistant_text, audio, {"channel": decision.channel})

            result.update(self.output_router.as_dict(routed))
            return result

        except Exception as exc:
            logger.error(f"LINGUIX Premium error: {exc}", exc_info=True)
            
            # Fallback to basic response
            return self._get_fallback_response(messages, language, user_level, user_name, speak)

    def _get_fallback_response(self, messages: List[Dict[str, str]], language: str, user_level: str, user_name: str, speak: bool) -> Dict[str, Any]:
        """Fallback response when premium mode unavailable."""
        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = (msg.get("content") or "").strip()
                break

        lowered = last_user.lower()
        assistant_text = ""

        # Context-aware fallback responses
        if any(token in lowered for token in ["explique", "comprendre", "comment", "c'est quoi", "definition"]):
            assistant_text = (
                f"Bonjour {user_name}! Voici une explication simple pour {user_level}:\n\n"
                "Une fraction represente une partie d'un tout. "
                "Par exemple, si on partage 8 sacs de sorgho et qu'on en garde 3, "
                "la partie gardee est 3/8 et la partie envoyee au marche est 5/8.\n\n"
                "Methode simple:\n"
                "1) Compte le total.\n"
                "2) Compte la partie qui t'interesse.\n"
                "3) Ecris: partie/total.\n\n"
                "Si tu veux, je peux te donner 3 petits exercices corriges."
            )
        elif any(token in lowered for token in ["exercice", "exercise", "exo", "problem"]):
            assistant_text = (
                f"Voici un exercice rapide de fractions pour {user_level}:\n\n"
                "Kossi a 8 sacs de sorgho. Il en garde 3 pour la maison. "
                "Quelle fraction des sacs va au marche?\n"
                "A) 3/8  B) 5/8  C) 6/8  D) 8/8\n\n"
                "Reponse: B) 5/8, car 8 - 3 = 5 sacs vont au marche."
            )
        elif any(token in lowered for token in ["salut", "bonjour", "hello", "bonsoir", "ça va"]):
            assistant_text = (
                f"Bonjour {user_name}! 👋\n\n"
                "Je suis ton assistant pédagogique SmartClasse. "
                "Je peux t'aider avec:\n"
                "• Des explications claires\n"
                "• Des exercices pratiques\n"
                "• Des corrections détaillées\n\n"
                "Qu'est-ce que tu veux apprendre aujourd'hui?"
            )
        else:
            assistant_text = (
                f"Salut {user_name}! Je comprends ta question.\n\n"
                "Peux-tu me donner plus de details? Par exemple:\n"
                "• Quel sujet? (math, francais, histoire...)\n"
                "• Qu'est-ce que tu veux? (explication, exercice, correction)\n\n"
                "Je serai plus utile avec plus de contexte!"
            )

        result: Dict[str, Any] = {
            "assistant_text": assistant_text,
            "intent": "fallback",
            "confidence": 0.0,
            "quality_score": 60.0,
            "fallback_mode": True,
        }

        if speak:
            audio = self._generate_audio(assistant_text, language)
            result.update({"audio_url": audio.get("audio_url"), "audio_path": audio.get("audio_path")})

        return result

    def detect_language(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        local_scores = {
            "french": ["bonjour", "école", "élève", "fraction", "marché", "famille"],
            "ewe": ["keka", "gbo", "sukulu", "dɔme", "miawo"],
            "kabyie": ["ag-ar", "fed", "sorgho", "karité"],
            "haoussa": ["makaranta", "kasuwa", "iyali", "karanta"],
            "mina": ["sɔ", "sukulu", "agbadza"],
            "tem": ["kpɔ", "gbɔ", "sɔ"],
        }

        best_language = "french"
        best_score = -1
        for language, keywords in local_scores.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_language = language
                best_score = score

        if detect is not None:
            try:
                detected = detect(text)
                if detected.startswith("fr"):
                    best_language = "french"
            except Exception:
                pass

        alternatives = [
            {"language": language, "confidence": 0.2 if language != best_language else 0.8}
            for language in self.SUPPORTED_LANGUAGES
            if language != best_language
        ]

        return {
            "detected_language": best_language,
            "confidence": 0.85 if best_score >= 0 else 0.55,
            "alternatives": alternatives[:2],
        }

    def get_supported_languages(self) -> Dict[str, Dict]:
        return self.SUPPORTED_LANGUAGES

    def measure_french_progression(self, student_id: str, week_number: int) -> Dict[str, Any]:
        french_percentage = min(20 + (week_number - 1) * 5, 80)
        local_percentage = 100 - french_percentage

        return {
            "student_id": student_id,
            "week": week_number,
            "language_mix": {
                "french_percent": french_percentage,
                "local_language_percent": local_percentage,
            },
            "recommendation": "increase_french" if week_number > 1 else "keep_current",
        }

    def create_multilingual_exercise(
        self,
        exercise_dict: Dict,
        primary_language: str,
        include_languages: List[str] = None,
    ) -> Dict[str, Any]:
        if include_languages is None:
            include_languages = ["french", primary_language]

        multilingual_exercise = {"exercise_id": exercise_dict.get("exercise_id"), "languages": {}}
        for lang in include_languages:
            multilingual_exercise["languages"][lang] = {
                "instruction": self._translate_via_gemma4(exercise_dict.get("instruction", ""), "french", lang),
                "problem": self._translate_via_gemma4(exercise_dict.get("problem", ""), "french", lang),
                "audio": self._generate_audio(exercise_dict.get("problem", ""), lang),
            }

        logger.info(f"LINGUIX: Multilingual exercise created | Languages: {include_languages}")
        return multilingual_exercise

    def voice_pipeline(
        self,
        audio_path: str,
        target_languages: List[str],
        source_language_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        transcription = self.transcribe(audio_path, language_hint=source_language_hint)
        detected_language = transcription.get("language_hint") or transcription.get("language_detected") or "french"

        translations = self.translate_instruction(
            instruction=transcription.get("text", ""),
            source_language=detected_language,
            target_languages=target_languages,
            audio_output=True,
        )

        return {
            "transcription": transcription,
            "translations": translations,
            "source_language": detected_language,
            "target_languages": target_languages,
        }

    def chat_voice(
        self,
        audio_bytes: Optional[bytes] = None,
        audio_path: Optional[str] = None,
        language_hint: Optional[str] = None,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        speak: bool = True,
    ) -> Dict[str, Any]:
        """Voice chat pipeline: VAD -> Normalizer -> ASR -> ContextHub -> Gemma -> TTS

        Returns a dict similar to chat(): assistant_text, intent, quality_score, audio metadata when speak=True.
        """
        try:
            # Load audio bytes if path provided
            if audio_path and audio_bytes is None:
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()

            if not audio_bytes:
                return {"status": "error", "detail": "No audio provided"}

            # Normalize audio and convert to PCM16 bytes for WebRTC VAD compatibility.
            norm = self.normalizer.process(audio_bytes)
            audio_np = norm.get("audio")
            sample_rate = int(norm.get("sample_rate") or 16000)
            vad_input = audio_bytes

            if isinstance(audio_np, np.ndarray) and audio_np.size > 0:
                clipped = np.clip(audio_np, -1.0, 1.0)
                vad_input = (clipped * 32767.0).astype(np.int16).tobytes()

            vad_failed = False
            try:
                vad_result = self.vad.process(vad_input, sample_rate=sample_rate)
            except Exception as exc:
                # Continue with ASR when VAD cannot parse the frame format.
                logger.warning(f"chat_voice: VAD failed, fallback to ASR | {exc}")
                vad_failed = True
                vad_result = None

            if not vad_failed and vad_result is not None and not vad_result.speech_detected:
                return {"status": "no_speech", "detail": "No speech detected"}

            # ASR transcription
            transcription = self.asr.transcribe(audio_bytes, language=language_hint, streaming=False)
            user_text = transcription.text if transcription and transcription.text else ""

            # Update context
            sess = user_id or f"guest_{uuid.uuid4().hex[:8]}"
            self.context_hub.add_turn(role="user", content=user_text, channel="voice")

            # Call Gemma via wrapper
            messages = [{"role": "user", "content": user_text}]
            try:
                resp = self.gemma.generate(messages=messages, channel="voice", max_tokens=150, temperature=0.6)
                # Ollama/call_chat returns dict with message.content
                assistant_text = ""
                if isinstance(resp, dict):
                    assistant_text = resp.get("message", {}).get("content") or resp.get("message") or resp.get("result") or str(resp)
                    if isinstance(assistant_text, dict):
                        assistant_text = assistant_text.get("content", "")
                    assistant_text = str(assistant_text).strip()
                else:
                    assistant_text = str(resp)
            except Exception as e:
                logger.warning(f"chat_voice: Gemma generate failed: {e}")
                assistant_text = "Désolé, je ne peux pas répondre pour le moment."

            # Update memory with assistant turn
            self.context_hub.add_turn(role="assistant", content=assistant_text, channel="voice")

            result = {
                "assistant_text": assistant_text,
                "transcription": {"text": user_text, "language": transcription.language if transcription else language_hint},
                "session_id": sess,
                "intent": "voice",
                "channel": "voice",
                "channel_confidence": 1.0,
                "channel_reason": "audio_payload_present",
            }

            # Generate audio if requested
            if speak:
                tts_meta = self.tts.synthesize(assistant_text)
                result.update({"audio": tts_meta})

            routed = self.output_router.route_voice_stream(assistant_text, result.get("audio"), {"channel": "voice"}) if speak else self.output_router.route_voice(assistant_text, result.get("audio"), {"channel": "voice"})
            result.update(self.output_router.as_dict(routed))

            return {"status": "success", "result": result}

        except Exception as exc:
            logger.error(f"chat_voice pipeline failed: {exc}", exc_info=True)
            return {"status": "error", "detail": str(exc)}

