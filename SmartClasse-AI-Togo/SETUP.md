# SETUP.md — Installation Instructions pour SmartClasse

## Prérequis

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Ollama** (pour Gemma 4 offline) — [Download](https://ollama.ai)
- **Git** — [Download](https://git-scm.com)

## 1️⃣ Cloner le Repository

```bash
git clone https://github.com/[YourUsername]/SmartClasse.git
cd SmartClasse
```

## 2️⃣ Setup Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## 3️⃣ Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4️⃣ Télécharger Gemma 4 E4B

### Option A : Via Ollama (Recommandé)

```bash
# Installer Ollama
# Windows/Mac/Linux: https://ollama.ai/download

# Télécharger Gemma 4 E4B (3.9 GB)
ollama pull gemma4:e4b

# Vérifier
ollama list
# Vous devez voir: gemma4:e4b

# Lancer le serveur Ollama (background)
ollama serve
# Ollama tournera sur http://localhost:11434
```

### Option B : Via Hugging Face (Alternative)

```bash
# Télécharger directement
huggingface-cli download google/gemma-4-e4b-it --local-dir ./models/gemma4

# Puis configurer HUGGINGFACE_PATH dans .env
```

## 5️⃣ Configurer Variables d'Environnement

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos paramètres
# Important: Laisser OLLAMA_BASE_URL=http://localhost:11434
```

## 6️⃣ Lancer l'API FastAPI

```bash
# Terminal 1: Démarrer Ollama
ollama serve

# Terminal 2: Démarrer l'API
uvicorn src.main:app --reload --port 8000
# API disponible à: http://localhost:8000

# Docs automatique: http://localhost:8000/docs
```

## 7️⃣ Tester les Agents

### ADAPTIX — Générer un Exercice

```bash
curl -X POST http://localhost:8000/agents/adaptix/generate \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "Kossi",
    "level": "CM1",
    "subject": "math",
    "topic": "fractions",
    "language": "kabyie"
  }'
```

### LINGUIX — Traduire une Instruction

```bash
curl -X POST http://localhost:8000/agents/linguix/translate_instruction \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Calculez le quart de 48",
    "source_language": "french",
    "target_languages": ["kabyie", "ewe", "haoussa"],
    "audio_output": true
  }'
```

### Santé Check

```bash
curl http://localhost:8000/health
```

## 📊 Vérifier le Setup

```bash
# Vérifier Python
python --version

# Vérifier pip packages
pip list | grep -E "fastapi|ollama|transformers|whisper"

# Vérifier Ollama
ollama list | grep gemma4

# Vérifier API
curl http://localhost:8000/
```

## 🐛 Troubleshooting

### Ollama timeout

```
Error: connect to localhost:11434
```

**Solution**: Assurez-vous que `ollama serve` tourne dans un autre terminal

### GPU/CUDA issues

```
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Audio module error

```bash
pip install librosa soundfile
```

### Permission denied (macOS/Linux)

```bash
chmod +x src/*.py
```

## 🎯 Prochaines Étapes

1. ✅ Setup complet
2. ⏭️ Lancer tests des agents
3. ⏭️ Intégrer données pédagogiques (MEPS curriculum)
4. ⏭️ Construire démo vidéo
5. ⏭️ Soumettre à Kaggle

---

**Questions?** Consultez [README.md](README.md) ou l'[API Docs](http://localhost:8000/docs)
