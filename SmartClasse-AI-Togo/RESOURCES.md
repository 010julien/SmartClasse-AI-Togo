# 🔗 RESOURCES.md — Liens Critiques pour SmartClasse

## 📌 HACKATHON

- **Kaggle Hackathon Page**: https://www.kaggle.com/competitions/gemma-4-good-hackathon
- **Règles Officielles**: https://www.kaggle.com/competitions/gemma-4-good-hackathon/rules
- **Deadline**: May 18, 2026 — 23:59 UTC
- **Prize Pool**: $200,000 USD
  - Main Track: $100K (1st: $50K, 2nd: $25K, 3rd: $15K, 4th: $10K)
  - Impact Track: $50K (Health: $10K, Resilience: $10K, Education: $10K, Equity: $10K, Security: $10K)
  - Technology Track: $50K (Cactus: $10K, LiteRT: $10K, llama.cpp: $10K, Ollama: $10K, Unsloth: $10K)

---

## 🤖 GEMMA 4 RESOURCES

### Download & Setup

- **Ollama (Recommended)**: https://ollama.ai
- **Hugging Face Hub**: https://huggingface.co/google/gemma-4
- **Google AI Studio**: https://aistudio.google.com (test before coding)
- **Gemma 4 Docs**: https://github.com/google/gemma

### Model Variants

- **E2B** (small) — 2B params, 1.2 GB, fast, mobile-friendly
- **E4B** (recommended) — 4B params, 3.9 GB, balanced
- **26B** (large) — 26B params, better quality but slower
- **31B** (largest) — 31B params, best quality

### Implementation Libraries

- **Ollama**: https://ollama.ai (easiest for local)
- **llama.cpp**: https://github.com/ggerganov/llama.cpp (efficient)
- **LiteRT**: https://ai.google.dev/edge
- **Unsloth**: https://github.com/unslothai/unsloth (fine-tuning)

---

## 🎙 AUDIO RESOURCES

### Speech Recognition (Transcription)

- **OpenAI Whisper**: https://github.com/openai/whisper
  - Supports 99+ languages including Togolese languages
  - Offline, no API key needed
  - Python: `pip install openai-whisper`

### Text-to-Speech (Offline)

- **pyttsx3**: https://pypi.org/project/pyttsx3 (offline, works offline)
- **Google TTS** (online option): https://cloud.google.com/text-to-speech
- **Edge TTS** (Copilot voices): https://github.com/rany2/edge-tts

### Audio Processing

- **Librosa**: https://librosa.org (feature extraction)
- **SoundFile**: https://soundfile.readthedocs.io (WAV/FLAC I/O)
- **Scipy**: https://scipy.org (signal processing)

---

## 📚 EDUCATION DATA SOURCES (Togo)

### Official Sources

- **MEPS Togo**: https://meps.gouv.tg (Ministère de l'Éducation)
- **UNESCO RESEN**: http://uis.unesco.org (Regional data)
- **Global Partnership Education (GPE)**: https://www.globalpartnership.org/togo
- **Pacte GPE Togo 2024**: October 2024 document (cited in proposal)

### Research Databases

- **Afrobarometer**: https://www.afrobarometer.org (survey data)
- **UNICEF Data**: https://data.unicef.org (health + education)
- **World Bank EdStats**: https://datatopics.worldbank.org/education

### Language Resources

- **Togolese Languages on Wikipedia**:
  - Kabiyè: https://en.wikipedia.org/wiki/Kabye_language
  - Ewe: https://en.wikipedia.org/wiki/Ewe_language
  - Haoussa: https://en.wikipedia.org/wiki/Hausa_language
  - Mina: https://en.wikipedia.org/wiki/Mina_language
  - Tem: https://en.wikipedia.org/wiki/Tem_language

---

## 💻 DEVELOPMENT TOOLS

### Python Setup

- **Python**: https://python.org (3.10+)
- **Anaconda**: https://anaconda.com (alternative environment manager)
- **PyCharm Community**: https://jetbrains.com/pycharm (IDE)

### Git & GitHub

- **Git**: https://git-scm.com
- **GitHub**: https://github.com
- **GitHub Desktop**: https://desktop.github.com (GUI)

### API & Testing

- **FastAPI**: https://fastapi.tiangolo.com
- **Uvicorn**: https://www.uvicorn.org
- **Postman**: https://postman.com (API testing)
- **curl**: Built-in (command-line HTTP)

### Code Quality

- **Black**: https://black.readthedocs.io (formatting)
- **Flake8**: https://flake8.pycqa.org (linting)
- **Pytest**: https://pytest.org (testing)
- **MyPy**: https://www.mypy-lang.org (type checking)

---

## 🎬 VIDEO RESOURCES

### Recording & Editing

- **OBS Studio**: https://obsproject.com (free, powerful)
- **ScreenFlow** (Mac): https://www.telestream.net/screenflow
- **Camtasia**: https://camtasia.com (easy, paid)
- **DaVinci Resolve**: https://www.blackmagicdesign.com/davinci-resolve (free editing)

### YouTube Upload

- **YouTube**: https://youtube.com/upload
- **YT-DLP**: https://github.com/yt-dlp/yt-dlp (download reference videos)

---

## 📊 DEPLOYMENT OPTIONS

### Live Demo (for jury)

- **Hugging Face Spaces**: https://huggingface.co/spaces (free, includes Gradio/Streamlit)
- **Replit**: https://replit.com (simple Python hosting)
- **Render**: https://render.com (free tier available)
- **Railway**: https://railway.app

### Code Hosting

- **GitHub**: https://github.com (primary)
- **Kaggle Datasets**: https://kaggle.com/datasets
- **Kaggle Notebooks**: https://kaggle.com/notebooks

---

## 📖 KAGGLE SUBMISSION TEMPLATE

```
Title:
EduPath AI: Offline Adaptive Education System for Togo

Category:
Future of Education

Summary (max 1500 words):
[Problem] + [Solution] + [Technical Implementation] + [Results] + [Impact]

Attachments Required:
1. Video (YouTube link) — 3 min max
2. Code (GitHub link) — public repository
3. Demo (Live link) — Hugging Face Spaces or similar
4. Repo License — Apache 2.0 (already in place)

Gallery:
- Cover image (recommended: 1920x1080px)
- Screenshots of agents working
- Architecture diagram
- Student impact story image
```

---

## 🎯 JUDGES' CRITERIA (100 points total)

| Criterion                   | Weight | Tips                                      |
| --------------------------- | ------ | ----------------------------------------- |
| **Impact & Vision** (40pts) | 40%    | Story > Tech. Show Kossi + Afissa + data  |
| **Video Quality** (30pts)   | 30%    | Live demo, clear audio, professional cuts |
| **Technical Depth** (30pts) | 30%    | Real code, real Gemma 4, reproducible     |

---

## 📞 SUPPORT & COMMUNITY

### Q&A Forums

- **Kaggle Forums**: https://kaggle.com/discussion
- **GitHub Issues**: Create in your repo
- **Stack Overflow**: https://stackoverflow.com (tag: gemma, langchain, ollama)

### Gemma 4 Community

- **Google AI Forum**: https://forums.developer.google.com (Google AI)
- **Ollama GitHub Issues**: https://github.com/ollama/ollama/issues

### Hackathon Community

- **Kaggle Discord** (if available): Check Kaggle site
- **Gemma 4 Discord**: Check Google AI website

---

## 📋 SUBMISSION CHECKLIST (Day 10)

Before submitting to Kaggle:

- [ ] Video recorded and uploaded to YouTube (unlisted)
- [ ] GitHub repo is PUBLIC with Apache 2.0 license
- [ ] README.md complete with setup instructions
- [ ] Code well-documented with comments
- [ ] All endpoints tested and working
- [ ] Demo link tested (Hugging Face Spaces or local accessible)
- [ ] Kaggle report written (< 1500 words)
- [ ] Cover image prepared (1920x1080px)
- [ ] All links verified (YouTube, GitHub, Demo)
- [ ] Submission created as "New Notebook"
- [ ] Category selected: "Future of Education"
- [ ] Submitted EARLY (Day 9, buffer for issues)

---

## 🔐 SECURITY NOTES

⚠️ **IMPORTANT**: Never commit these to GitHub:

- `.env` file (use `.env.example`)
- API keys or secrets
- Database files (SQLite)
- Personal data
- Model weights (unless explicitly allowed)

---

## 📈 SUCCESS TIMELINE

```
Day 1 (Today)     → Setup + Architecture (70% done)
Day 2-3           → Agents working live
Day 4-5           → DIAGNOSTIX + PILOTIX added
Day 6-7           → KULTURIX + PARENTIX integrated
Day 8             → Code polished + optimized
Day 9             → Video recorded + uploaded
Day 10            → Kaggle report + submit
(Deadline May 18)
```

---

**Good luck! 🚀**

Remember: The jury wants to see impact + code proof + live demo.

Your story (Kossi, Afissa, Frédéric) is your superpower.
