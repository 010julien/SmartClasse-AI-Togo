# SmartClasse AI Togo — Methodology

*This document satisfies hackathon rule 2.8: a reproducible description of the approach, architecture, preprocessing steps, hyperparameters, and reproduction instructions.*

---

## 1. Problem Framing

### Context
Togo has 3.2 million school-age children, 60%+ of rural schools without internet, and a teacher-to-student ratio of 1:80 in underserved districts. Existing EdTech solutions fail because they assume: (1) reliable internet, (2) French literacy, (3) Western cultural context.

### Design Constraints
- **Zero connectivity required** at inference time
- **Runs on commodity hardware** (Raspberry Pi 4, ~$50)
- **Multi-lingual** — French, English, Ewe, Kabiyè, Mina, Hausa
- **Curriculum-aligned** — follows official Togolese MEPS (Ministry of Education) program
- **Privacy-preserving** — no data leaves the device

---

## 2. System Architecture

### 2.1 Component Stack

```
Layer           Component               Purpose
──────────────  ──────────────────────  ──────────────────────────────────
Frontend        Flutter 3.x             Cross-platform mobile/web client
API             FastAPI + Uvicorn       REST API server
Inference       Ollama + Gemma 4 E4B   Local LLM inference (offline)
ASR             OpenAI Whisper (base)   Speech-to-text (local, CPU)
TTS             pyttsx3                 Text-to-speech (system voices)
Audio Pipeline  librosa + noisereduce   Audio preprocessing
Database        SQLite + SQLAlchemy     Student profiles (local file)
Config          Pydantic Settings       Environment-validated configuration
```

### 2.2 Multi-Agent Architecture

SmartClasse uses a **specialized multi-agent pattern**: each agent has a narrow, well-defined responsibility. The ORCHESTRATOR routes complex queries across multiple agents and synthesizes their outputs.

#### Agent Specifications

**ADAPTIX — Adaptive Content Generator**
- Input: student name, level (CP/CE1/CE2/CM1/CM2), subject, topic, language
- Output: structured JSON with lesson content, exercises, difficulty calibration
- Prompt strategy: curriculum-grounded generation with explicit level anchoring
- Temperature: 0.4 (moderate creativity, high coherence)

**LINGUIX — Language & Voice Processor**
- Subcomponents:
  - Transcription: Whisper `base` model (74M params, ~145MB), CPU inference
  - Translation: Gemma 4 E4B via Ollama with few-shot language prompts
  - TTS: pyttsx3 (system voices) — no API calls, no network
  - Chat: full conversational loop with language detection (langdetect)
- Audio preprocessing pipeline:
  1. Format normalization (pydub: any format → WAV 16kHz mono)
  2. Noise reduction (noisereduce: spectral subtraction)
  3. VAD segmentation (webrtcvad-wheels: aggressiveness level 2)
  4. Whisper inference (beam_size=5, best_of=5)

**DIAGNOSTIX — Learning Diagnostics**
- Input: student_id, student_name, level, language
- Loads historical interaction data from SQLite
- Output: structured JSON with identified strengths, learning gaps, risk indicators (0–1 float), recommended interventions
- Prompt strategy: chain-of-thought reasoning over student history

**PILOTIX — Teacher Dashboard**
- Aggregates diagnostic data across a class
- Output: per-subject coverage %, at-risk student list, curriculum gap analysis
- Designed for low-literacy teachers: simple numerical output

**EQUITIX — Inclusion & Equity**
- Detects potential learning disabilities (dyslexia, dyscalculia, attention)
- Generates IEP-style (Individual Education Plan) recommendations
- Uses standardized screening criteria adapted for sub-Saharan context

**PARENTIX — Family Communication**
- Generates concise progress summaries in the family's language
- SMS-compatible (≤160 chars per message, graceful degradation)
- Respects literacy level of parents (simple vocabulary mode)

**KULTURIX — Cultural Grounding**
- Retrieves relevant Togolese proverbs, examples, and analogies
- Grounds abstract concepts in local agricultural/social context
- Corpus: `data/cultural_corpus.json` (curated Togolese knowledge base)

**ORCHESTRATOR — Multi-Agent Router**
- Receives complex queries that span multiple domains
- Determines which agents to invoke and in what order
- Synthesizes outputs into a coherent, unified response
- Uses structured reasoning (chain-of-thought with explicit agent selection step)

---

## 3. Language Model Configuration

### Model: Gemma 4 E4B (via Ollama)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `gemma4:e4b` | 4B params, quantized — fits 4GB RAM |
| Temperature | 0.3 (default) | High accuracy for educational content |
| Max tokens | 2048 | Full lesson content without truncation |
| Context window | 8192 | Full conversation history |
| Timeout | 300s | Accommodates slow CPU inference |

Temperature is agent-specific:
- ADAPTIX generate: 0.4 (structured + creative)
- DIAGNOSTIX: 0.2 (factual, consistent)
- KULTURIX: 0.6 (generative, evocative)
- All others: 0.3

### Why Gemma 4 E4B
- Smallest Gemma 4 variant that handles multilingual tasks (including African languages) reliably
- Quantized (E4B = 4-bit embedding) — reduces memory footprint by ~60% vs FP16
- Runs on CPU with Ollama — no GPU required
- Apache 2.0 license — fully compliant with CC-BY 4.0 submission requirements

---

## 4. Prompt Engineering Strategy

### 4.1 System Prompt Structure
Each agent uses a structured system prompt with:
1. **Role definition**: "Tu es ADAPTIX, un agent pédagogique spécialisé..."
2. **Constraints**: language, curriculum alignment, output format
3. **Output schema**: explicit JSON structure the model must follow
4. **Few-shot examples** (2–3 examples for structured tasks)

### 4.2 JSON Extraction
Responses are parsed with a robust `extract_json()` function (`src/prompting.py`) that:
- First attempts direct JSON parsing
- Falls back to regex extraction from markdown code blocks
- Returns `None` on failure (logged at DEBUG level) — never crashes the endpoint

### 4.3 Cultural Grounding
KULTURIX prepends a culturally-relevant context block to ADAPTIX prompts when cultural grounding is enabled:
```
[Cultural context for {topic} in Togo]:
{retrieved_proverb_or_analogy}
Use this context to make the explanation relatable to Togolese students.
```

---

## 5. Audio Processing Pipeline

### 5.1 Input Processing (LINGUIX transcribe)
```
Raw audio (any format)
    → pydub: decode + resample to 16kHz mono WAV
    → noisereduce: spectral noise subtraction (stationary noise profile)
    → webrtcvad: VAD segmentation (aggressiveness=2)
    → Whisper base: transcription
    → langdetect: language identification
    → output: {"text": "...", "language": "fr", "confidence": 0.97}
```

### 5.2 Output Processing (TTS)
```
Text response
    → pyttsx3: select voice by language code
    → synthesize to WAV buffer
    → encode to base64
    → return in JSON response body (no file system dependency)
```

### 5.3 Full Voice Pipeline
```
Audio upload → transcription → LINGUIX chat → TTS → audio response
(complete round-trip: voice in, voice out)
```

---

## 6. Data

### 6.1 MEPS Curriculum (`data/meps_curriculum.json`)
Structure:
```json
{
  "level": "CE1",
  "subject": "Mathématiques",
  "topics": [
    {
      "name": "Additions et soustractions jusqu'à 100",
      "competences": [...],
      "prerequis": [...],
      "progression": "Trimestre 1"
    }
  ]
}
```
Source: Togolese Ministry of Education (MEPS) official program documents. No personally identifiable information.

### 6.2 Cultural Corpus (`data/cultural_corpus.json`)
Curated collection of:
- Togolese proverbs (Ewe, Kabiyè, French translations)
- Agricultural analogies (farming cycles, market concepts)
- Social context examples (community, family structures)

---

## 7. Database Schema

SQLite with SQLAlchemy ORM. Three tables:

```sql
students (id TEXT PK, name TEXT, level TEXT, language TEXT, created_at DATETIME)
interactions (id INT PK, student_id FK, agent TEXT, query TEXT,
              response TEXT, timestamp DATETIME, duration_ms INT)
profiles (student_id FK PK, strengths JSON, gaps JSON, risk_score FLOAT,
          last_updated DATETIME)
```

Optional AES-256 encryption via SQLCipher (`DATABASE_ENCRYPT=True`).

---

## 8. Security Design

| Control | Implementation |
|---------|---------------|
| CORS | Explicit origin whitelist (no `*`) |
| Input validation | Pydantic v2 models on all POST endpoints — 422 on invalid input |
| Temp file cleanup | try/finally ensures deletion even on exception |
| Error messages | Generic messages to client; full stack trace logged server-side only |
| Encryption | AES-256 SQLite encryption in production mode |
| No secrets in code | All config via environment variables with `pydantic-settings` |

---

## 9. Reproduction Instructions

### Complete Reproduction (from scratch)

```bash
# 1. Clone the repository
git clone https://github.com/010julien/SmartClasse-AI-Togo.git
cd SmartClasse-AI-Togo

# 2. Install Ollama (https://ollama.com) then:
ollama pull gemma4:e4b
ollama serve &

# 3. Create Python environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# 4. Install PyTorch (CPU) — must precede other deps
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 5. Install remaining dependencies
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
# Edit .env as needed (defaults work for local development)

# 7. Start the backend
uvicorn src.main:app --host 0.0.0.0 --port 8000

# 8. Verify
curl http://localhost:8000/health
```

### Kaggle Notebook Reproduction

Open `kaggle_submission.ipynb` in Kaggle Notebooks. The notebook:
- Auto-detects whether Ollama is available
- Falls back to pre-computed demo responses if not (for evaluators)
- Demonstrates all 8 agents with realistic inputs
- Verifies the offline capability matrix

### Running Tests

```bash
pytest tests/ -v
# 35 integration tests covering all endpoints
# Tests use mocked agents — no Ollama required
```

### Expected Resource Usage

| Resource | Value |
|----------|-------|
| RAM (inference) | ~3.5 GB (Gemma 4 E4B) |
| Disk (model) | ~2.8 GB (Ollama model cache) |
| CPU (inference) | 4 cores, ~30s for first response, <3s cached |
| Disk (app) | ~500 MB (including venv) |
| Network | Zero (fully offline after setup) |

---

## 10. Limitations and Future Work

### Current Limitations
- Whisper `base` model has lower accuracy for Ewe/Kabiyè than French — would benefit from fine-tuning
- pyttsx3 TTS has no African-language voices on most systems — voice output defaults to French
- Cultural corpus is manually curated — limited coverage outside major ethnic groups
- PARENTIX SMS integration is stubbed (no live SMS gateway in the demo)

### Fine-Tuning Roadmap
See `unsloth_finetune.ipynb` for a complete fine-tuning pipeline using Unsloth:
- Dataset: synthetic student-teacher dialogues in Ewe and Kabiyè
- Base model: Gemma 4 E4B
- Method: QLoRA (4-bit quantization, LoRA rank 16)
- Target improvement: Ewe/Kabiyè comprehension accuracy +40%

### Scaling Path
1. **Phase 1 (current)**: Single-device deployment per school
2. **Phase 2**: Local LAN mesh — one server, 30 tablets per school
3. **Phase 3**: Sync-on-connectivity — periodic national curriculum updates via USB/sneakernet

---

*This methodology document was prepared in compliance with hackathon rule 2.8 requiring a reproducible description of the submitted system.*
