# QUICK_START.md — Démarrer en 5 minutes

## 🚀 Démarrage Rapide SmartClasse

### Prérequis Absolus

- Python 3.10+
- 4 GB RAM minimum
- 10 GB disque libre (pour Gemma 4)

### Step 1: Clone & Setup (2 min)

```bash
# Clone
git clone https://github.com/[YourUsername]/SmartClasse.git
cd SmartClasse

# Virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

### Step 2: Download Gemma 4 (5-10 min with good internet)

```bash
# Install Ollama: https://ollama.ai
# Then download Gemma 4
ollama pull gemma4:e4b

# Start Ollama (new terminal)
ollama serve
```

### Step 3: Run API (1 min)

```bash
# Terminal 2
uvicorn src.main:app --reload --port 8000

# Visit http://localhost:8000/docs
```

### Step 4: Test Agents (1 min)

```bash
# Test ADAPTIX
curl -X POST http://localhost:8000/agents/adaptix/generate \
  -H "Content-Type: application/json" \
  -d '{"student_name":"Kossi","level":"CM1","subject":"math","topic":"fractions","language":"kabyie"}'

# Expected: Exercise in Kabyie about sorghum fractions
```

### Step 5: Test LINGUIX

```bash
# Translate instruction
curl -X POST http://localhost:8000/agents/linguix/translate_instruction \
  -H "Content-Type: application/json" \
  -d '{"instruction":"Calculez le quart de 48","source_language":"french","target_languages":["kabyie","ewe","haoussa"]}'

# Expected: Translations in 3 languages + audio files
```

---

## ✅ If Everything Works

You should see:

- ✅ ADAPTIX generating math exercise with sorghum context in Kabyie
- ✅ LINGUIX translating to multiple languages
- ✅ API responding with JSON
- ✅ Ollama running smoothly

**Next**: Build demo + video + submit to Kaggle

---

## 🆘 If Issues

**Ollama not found?**

```bash
# Reinstall Ollama from https://ollama.ai
# Restart terminal after install
```

**Audio module error?**

```bash
pip install librosa soundfile --force-reinstall
```

**Torch/CUDA error?**

```bash
# Use CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Need help?** Check SETUP.md or issues on GitHub
