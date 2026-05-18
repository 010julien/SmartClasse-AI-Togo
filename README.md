# SmartClasse AI Togo

> **AI-powered adaptive education for 3.2 million children in West Africa — fully offline, local-first, multi-lingual.**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)](https://flutter.dev)
[![Ollama](https://img.shields.io/badge/Ollama-Gemma%204%20E4B-orange)](https://ollama.com)

---

## The Problem

In Togo (West Africa), **3.2 million school-age children** face a structural education crisis:

- **60%+ of rural schools** have no internet connectivity
- **Teacher-to-student ratio**: 1:80 in many rural districts
- **6 national languages** in active use — but curricula only exist in French
- **12% of children** with learning disabilities receive no adapted support
- **Low-income families** cannot afford tutoring or supplementary materials

Standard EdTech solutions fail here: they require connectivity, assume French literacy, and ignore local cultural context.

---

## The Solution

**SmartClasse AI** is an **offline-first, multi-agent AI tutoring system** that runs entirely on a local device — no cloud, no subscription, no connectivity required.

It adapts to each student's level, speaks their language (including Ewe, Kabiyè, Mina), follows the official Togolese MEPS curriculum, and provides teachers with real-time diagnostic dashboards.

---

## Prize Track Positioning

| Track | Relevance | Key Features |
|-------|-----------|--------------|
| **Ollama — $10k** | Primary track | Entire inference stack runs via Ollama (Gemma 4 E4B); zero cloud calls |
| **Future of Education — $10k** | Core mission | Adaptive tutoring, curriculum alignment (MEPS), learning diagnostics |
| **Digital Equity — $10k** | Design principle | Offline-first, low-bandwidth, multi-lingual (6 languages) |
| **Global Resilience — $10k** | Deployment model | Works in power-unstable, connectivity-zero rural Togo |
| **Cactus — $10k** | Architecture | Multi-agent system with structured reasoning and tool orchestration |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Flutter Client (Mobile/Web)            │
│   Voice Input → Transcription → Response → TTS Output   │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / REST
┌──────────────────────────▼──────────────────────────────┐
│                FastAPI Backend (Python 3.10+)            │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ ADAPTIX  │  │ LINGUIX  │  │DIAGNOSTIX│  │PILOTIX │  │
│  │(Adaptive │  │(Language │  │(Learning │  │(Teacher│  │
│  │ Content) │  │ + Voice) │  │ Analysis)│  │Dashboard│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       └─────────────┴─────────────┴─────────────┘       │
│                         │ ORCHESTRATOR                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ EQUITIX  │  │PARENTIX  │  │ KULTURIX │               │
│  │(Inclusion│  │(Family   │  │(Cultural │               │
│  │ Support) │  │ Alerts)  │  │  Context)│               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       └─────────────┴─────────────┘                      │
└──────────────────────────┬──────────────────────────────┘
                           │ Ollama API (local)
┌──────────────────────────▼──────────────────────────────┐
│           Gemma 4 E4B (via Ollama — local inference)     │
│        Whisper Base (ASR) │ pyttsx3 (TTS, offline)       │
└─────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Function |
|-------|----------|
| **ADAPTIX** | Generates differentiated lessons adapted to the student's level and profile |
| **LINGUIX** | Handles speech-to-text, translation, TTS, and multilingual chat (6 languages) |
| **DIAGNOSTIX** | Produces learning diagnostics: strengths, gaps, risk indicators |
| **PILOTIX** | Teacher-facing dashboard: class progress, at-risk alerts, curriculum coverage |
| **EQUITIX** | Detects learning disabilities, generates inclusion plans |
| **PARENTIX** | Sends progress summaries to parents via SMS (offline-compatible) |
| **KULTURIX** | Grounds explanations in local Togolese cultural context and proverbs |
| **ORCHESTRATOR** | Routes complex queries across multiple agents with structured reasoning |

---

## Key Technical Features

### Offline-First by Design
- **No internet required at inference time** — Ollama runs Gemma 4 E4B locally
- SQLite database — no external DB server needed
- Whisper ASR runs locally on CPU
- pyttsx3 TTS uses system voices — no API calls

### Multi-Lingual Support
Languages handled: **French, English, Ewe, Kabiyè, Mina, Hausa**

### Curriculum Alignment
Lessons and diagnostics follow the official **Togolese MEPS curriculum** (`data/meps_curriculum.json`) — not a generic Western curriculum.

### Privacy by Default
- All student data stays on the local device
- Optional AES encryption for the SQLite database (`DATABASE_ENCRYPT=True`)
- No telemetry, no data exfiltration

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed locally
- (Optional) Flutter SDK for mobile/web client

### 1. Install Ollama and pull the model
```powershell
# Install Ollama from https://ollama.com
ollama pull gemma4:e4b
ollama serve
```

### 2. Set up the Python backend
```powershell
# In the SmartClasse-AI-Togo directory
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install PyTorch first (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install all other dependencies
pip install -r requirements.txt
```

### 3. Configure environment
```powershell
copy .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 4. Launch the backend
```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Verify
```powershell
Invoke-RestMethod http://localhost:8000/health
# → {"status": "healthy", "agents": [...]}
```

### 6. Launch Flutter client (optional)
```bash
cd flutter_client
flutter pub get
flutter run -d chrome
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health + agent status |
| POST | `/agents/adaptix/generate` | Generate adaptive lesson content |
| POST | `/agents/adaptix/evaluate` | Evaluate student response |
| POST | `/agents/diagnostix/analyze` | Full learning diagnostic |
| POST | `/agents/linguix/chat` | Multilingual text chat |
| POST | `/agents/linguix/transcribe` | Speech-to-text (audio upload) |
| POST | `/agents/linguix/tts` | Text-to-speech synthesis |
| POST | `/agents/linguix/voice_pipeline` | Full voice pipeline (ASR → LLM → TTS) |
| POST | `/agents/pilotix/dashboard` | Teacher dashboard data |
| POST | `/agents/equitix/risk` | Inclusion/disability risk assessment |
| POST | `/agents/orchestrator/generate` | Multi-agent orchestrated response |
| GET | `/docs` | Interactive API documentation (Swagger) |

---

## Impact Metrics

| Metric | Value |
|--------|-------|
| Target population | 3.2M school-age children in Togo |
| Languages supported | 6 (French, English, Ewe, Kabiyè, Mina, Hausa) |
| Curriculum coverage | Full MEPS primary school curriculum |
| Infrastructure required | Raspberry Pi 4 or equivalent (4GB RAM) |
| Internet required | None (fully offline) |
| Cost per school | ~$50 one-time hardware (vs. $0 software) |
| Agent response time | <3s on CPU (Gemma 4 E4B quantized) |

---

## Project Structure

```
SmartClasse-AI-Togo/
├── src/
│   ├── main.py              # FastAPI app, all endpoints
│   ├── config.py            # Settings with Pydantic validation
│   ├── agents/
│   │   ├── adaptix.py       # Adaptive content generation
│   │   ├── linguix.py       # Language + voice processing
│   │   ├── diagnostix.py    # Learning diagnostics
│   │   ├── pilotix.py       # Teacher dashboard
│   │   ├── equitix.py       # Inclusion support
│   │   ├── parentix.py      # Family communication
│   │   ├── kulturix.py      # Cultural grounding
│   │   └── orchestrator.py  # Multi-agent routing
│   ├── audio/               # Audio processing pipeline
│   └── db.py                # SQLite ORM
├── flutter_client/          # Cross-platform mobile/web UI
├── data/
│   ├── meps_curriculum.json # Official Togolese curriculum
│   └── cultural_corpus.json # Togolese cultural knowledge base
├── tests/
│   ├── conftest.py
│   └── test_api.py          # 35 FastAPI integration tests
├── kaggle_submission.ipynb  # Kaggle demo notebook
├── unsloth_finetune.ipynb   # Fine-tuning notebook (Unsloth track)
├── METHODOLOGY.md           # Reproducible methodology (rule 2.8)
├── requirements.txt
├── LICENSE                  # CC-BY 4.0 + Apache 2.0
└── NOTICE.txt               # Third-party licenses
```

---

## Running Tests

```powershell
pytest tests/ -v
```

---

## Reproducibility

See [METHODOLOGY.md](METHODOLOGY.md) for the complete methodology description, including architecture decisions, hyperparameters, preprocessing steps, and reproduction instructions — as required by hackathon rule 2.8.

---

## License

This project is dual-licensed:
- **Creative Commons Attribution 4.0 International (CC-BY 4.0)** — for documentation, datasets, and notebooks
- **Apache License 2.0** — for source code

See [LICENSE](LICENSE) and [NOTICE.txt](NOTICE.txt) for full details and third-party attributions.

---

## Team

**SmartClasse AI** — Built for the Kaggle x Gemma Hackathon 2025

*Empowering every child in Togo with personalized AI education — regardless of connectivity, language, or economic background.*
