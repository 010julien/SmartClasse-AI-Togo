# ✅ IMMEDIATE ACTIONS — Right Now (Next 2 Hours)

## 🎯 Critical Path for TODAY

### Step 1: Kaggle Registration (5 min) — DO NOW

```
1. Visit: https://www.kaggle.com/competitions/gemma-4-good-hackathon
2. Sign in (or Register if needed)
3. Click: "Join Hackathon"
4. Accept rules
5. Confirm account if prompted
✅ DONE: You're registered
```

### Step 2: GitHub Repository (10 min) — DO NOW

```
1. Go to: https://github.com/new
2. Repository name: EduPath-AI-Togo
3. Description: Offline Adaptive Education System for Togo
4. Visibility: PUBLIC ← CRITICAL
5. License: Apache 2.0 ← CRITICAL
6. Click: "Create repository"
✅ DONE: Repo created
```

### Step 3: Push Code to GitHub (5 min) — DO NOW

```powershell
# Open PowerShell
cd "c:\Users\DELL\Desktop\SmartClasse-AI-Togo\EduPath-AI-Togo"

# Copy these commands EXACTLY:
git init
git add .
git commit -m "Initial commit: EduPath AI - Kaggle Gemma 4 Good Hackathon"
git branch -M main

# GitHub will show you these after repo creation:
git remote add origin https://github.com/[YOUR_USERNAME]/EduPath-AI-Togo.git
git push -u origin main

# Verify:
git log --oneline
git remote -v

✅ DONE: Code on GitHub
```

### Step 4: Install Ollama (10 min) — START NOW

```
1. Go to: https://ollama.ai
2. Download for Windows
3. Install (follows installer)
4. Restart terminal after install
5. Verify:
   ollama --version
✅ DONE: Ollama installed
```

### Step 5: Download Gemma 4 E4B (15-30 min) — START NOW

```powershell
# This downloads 3.9 GB (depends on internet speed)
ollama pull gemma4:e4b

# Verify it downloaded:
ollama list

# You should see:
# gemma4:e4b latest abc123def456 3.9GB

✅ DONE: Gemma 4 ready
```

### Step 6: Setup Python (5 min) — DO NOW

```powershell
# In project directory
cd "c:\Users\DELL\Desktop\SmartClasse-AI-Togo\EduPath-AI-Togo"

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see: (venv) in prompt

# Upgrade pip
pip install --upgrade pip

# Install dependencies (5-10 min)
pip install -r requirements.txt

✅ DONE: Environment ready
```

---

## 🚀 Testing Phase (Next 30 min)

### Terminal Setup

```
You'll need 3 terminals open simultaneously:

Terminal 1: Ollama server (leave running)
Terminal 2: FastAPI server (leave running)
Terminal 3: Testing commands
```

### Terminal 1: Start Ollama

```powershell
# Terminal 1
ollama serve

# You should see:
# Listening on 127.0.0.1:11434
# (leave this running)
```

### Terminal 2: Start FastAPI

```powershell
# Terminal 2
cd "c:\Users\DELL\Desktop\SmartClasse-AI-Togo\EduPath-AI-Togo"
venv\Scripts\activate
uvicorn src.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

### Terminal 3: Test Endpoints

```powershell
# Terminal 3
cd "c:\Users\DELL\Desktop\SmartClasse-AI-Togo\EduPath-AI-Togo"

# Health check
curl http://localhost:8000/health

# Should return: {"status":"online","version":"0.1.0",...}

# Test ADAPTIX
curl -X POST http://localhost:8000/agents/adaptix/generate `
  -H "Content-Type: application/json" `
  -d '{
    "student_name":"Kossi",
    "level":"CM1",
    "subject":"math",
    "topic":"fractions",
    "language":"kabyie"
  }'

# Should return JSON exercise object

# Test LINGUIX
curl -X POST http://localhost:8000/agents/linguix/translate_instruction `
  -H "Content-Type: application/json" `
  -d '{
    "instruction":"Calculez le quart de 48",
    "source_language":"french",
    "target_languages":["kabyie","ewe","haoussa"],
    "audio_output":false
  }'

# Should return translations
```

---

## ✅ Success Criteria (End of Day 1)

You'll know you succeeded when:

- [x] Kaggle account shows you're registered for hackathon
- [x] GitHub repo exists and is public
- [x] Code is pushed to GitHub (git log shows commits)
- [x] Ollama server runs without errors
- [x] Gemma 4 E4B downloaded (ollama list shows it)
- [x] Python venv created and activated
- [x] Dependencies installed (pip list | grep fastapi works)
- [x] FastAPI starts without errors
- [x] /health endpoint returns JSON
- [x] /agents/adaptix/generate returns exercise
- [x] /agents/linguix/translate_instruction returns translations

---

## 🚨 Common Issues & Fixes

### "ollama: command not found"

```
→ Ollama not installed or restart terminal after install
→ Solution: Reinstall from https://ollama.ai
```

### "Connection refused" on localhost:11434

```
→ Ollama server not running
→ Solution: Run "ollama serve" in Terminal 1
```

### "Module not found" errors

```
→ Python dependencies not installed
→ Solution: Activate venv, run "pip install -r requirements.txt"
```

### Gemma 4 very slow

```
→ Using CPU instead of GPU
→ Solution: Normal for Gemma 4 E4B on CPU (still works, ~1-2s per response)
```

### Port 8000 already in use

```
→ Another app using port 8000
→ Solution: uvicorn src.main:app --reload --port 8001
```

---

## ⏰ Time Estimate

| Task                   | Time   | Total          |
| ---------------------- | ------ | -------------- |
| Kaggle signup          | 5 min  | 5 min          |
| GitHub repo            | 10 min | 15 min         |
| Git push               | 5 min  | 20 min         |
| Ollama install         | 10 min | 30 min         |
| Gemma 4 download       | 20 min | 50 min         |
| Python setup           | 5 min  | 55 min         |
| Dependencies           | 10 min | 65 min         |
| Ollama + FastAPI start | 5 min  | 70 min         |
| Testing                | 15 min | 85 min         |
| **TOTAL**              |        | **~1.5 hours** |

---

## 📱 Verification Checklist

After each step, verify:

```bash
# After Kaggle
✅ https://www.kaggle.com/competitions/gemma-4-good-hackathon
   shows "You've Joined"

# After GitHub
✅ https://github.com/[USERNAME]/EduPath-AI-Togo
   shows code in repo

# After Ollama
✅ ollama list
   shows "gemma4:e4b latest ..." with size

# After Python setup
✅ pip list | grep fastapi
   shows fastapi version

# After API start
✅ curl http://localhost:8000/health
   returns JSON with "online" status

# Final test
✅ http://localhost:8000/docs
   shows Swagger API documentation
```

---

## 🎯 Next Standup

**When**: Tomorrow morning or after completion  
**Status**: Report these:

1. ✅ Kaggle registration complete
2. ✅ GitHub repo created + code pushed
3. ✅ Ollama + Gemma 4 running
4. ✅ FastAPI accepting requests
5. ✅ ADAPTIX + LINGUIX endpoints tested

**If blocked**: Report specific error + solution attempted

---

## 📞 Quick Help

- FastAPI docs: http://localhost:8000/docs (after API starts)
- Ollama help: `ollama help`
- Python help: `python --help`
- Git help: `git --help`

---

**GO GO GO! 🚀 You've got this! The hardest part is done (architecture). Now it's just execution.**

Next update: Tomorrow with Jour 2 detailed plan (ADAPTIX + LINGUIX full integration with real Gemma 4)
