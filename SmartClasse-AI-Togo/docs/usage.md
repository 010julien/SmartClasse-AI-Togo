# SmartClasse — Guide d'utilisation rapide

Ce document donne des exemples d'appel et d'utilisation des endpoints principaux (chat texte, chat voix, transcription, TTS streaming, benchmark).

## Exécution Docker allégée (Ollama-first)

Le `Dockerfile` supporte maintenant un manifeste de dépendances sélectionnable au build via l'argument `REQUIREMENTS`.

Build backend allégé (manifeste `requirements.ollama.txt`):

```powershell
docker compose build backend --no-cache --build-arg REQUIREMENTS=requirements.ollama.txt
```

Recréer le service backend avec l'image fraîche:

```powershell
docker compose up -d --force-recreate backend
docker compose ps
Invoke-RestMethod http://127.0.0.1:8010/health
```

1. Chat (JSON)

POST /agents/linguix/chat
Content-Type: application/json
Body:
{
"messages": [{"role":"user","content":"Bonjour, explique les fractions"}],
"speak": false,
"language": "french",
"user_level": "CE1",
"user_id": "student_kossi_001",
"user_name": "Kossi"
}

Réponse: JSON contenant `assistant_text`, `intent`, `quality_score`, etc.

2. Chat voix (multipart/form-data)

POST /agents/linguix/chat
Content-Type: multipart/form-data
Fields:

- file: fichier WAV/MP3 (champ `file`)
- language: french (optionnel)
- user_id, user_name (optionnels)

Le serveur sauvegarde temporairement l'audio, appelle la pipeline VAD→ASR→LLM→TTS et renvoie `result` contenant `assistant_text` et métadonnées audio (champ `audio`).

Exemple curl (PowerShell):

$body = @{
file = Get-Item "C:\chemin\vers\sample.wav"
language = "french"
}
Invoke-RestMethod -Uri http://127.0.0.1:8010/agents/linguix/chat -Method Post -Form $body

3. Transcription

POST /agents/linguix/transcribe
Form-data: file (audio)
Réponse: objet `transcription` contenant `text`, `language_detected`, etc.

4. Voice pipeline (traduction + audio)

POST /agents/linguix/voice_pipeline
Form-data:

- file: audio
- source_language_hint: french
- target_languages: ewe,kabyie

Réponse: `transcription` + `translations` + métadonnées audio si demandé.

5. TTS streaming (prototype)

POST /agents/linguix/tts_stream
Content-Type: application/json
Body: { "text": "Bonjour Kossi" }

Réponse: flux audio `audio/wav` (streaming par chunks). C'est un proxy qui écrit d'abord un WAV temporaire, puis le sert en chunks — utile pour tests et intégration rapide.

6. Benchmark local (simulé)

Script: `scripts/bench_linguix.py` — exécute un benchmark simulé ASR→LLM→TTS (composants mockés) et affiche latences moyennes/min/max.

Lancer:

python scripts/bench_linguix.py

Mesures runtime observées (en local Docker, indicatif):

- `/health`: ~2-3 ms (cold start initial plus élevé)
- `/agents/linguix/chat` (texte): ~5.8s à 7.4s (latence dominée par l'inférence LLM)

7. Notes opérationnelles

- Si `gemma4:e4b` ne charge pas (erreur mémoire), augmenter la mémoire Docker Desktop ou utiliser le fallback quantifié (`llm_quantized`) si vous avez un modèle GGUF local.
- Les modules clefs:
  - `src/modules/audio_input` : VAD, ASR, normalisation
  - `src/modules/llm` : `gemma_engine` wrapper autour d'Ollama
  - `src/modules/audio_output` : `tts_engine` (prototype de streaming)
  - `src/modules/routing` : `channel_detector`, `output_router`

8. Étapes suggérées après tests

- Remplacer le `tts_engine` prototype par un moteur streaming natif (Coqui/Edge/Piper) pour réduire latence et supporter barge-in réel.
- Ajouter tests d'intégration end-to-end avec un modèle LLM léger pour mesurer la latence voix→voix réelle.

9. Démo voix validée (bout-à-bout)

Générer un sample audio puis lancer la démo:

```powershell
python scripts/gen_sample.py
python scripts/demo_voice_chat.py --file samples/sample.wav --host http://127.0.0.1:8010
```

Option voix plus réaliste (TTS local):

```powershell
python -c "import pyttsx3, os; os.makedirs('samples', exist_ok=True); p='samples\\speech.wav'; e=pyttsx3.init(); e.save_to_file('Bonjour SmartClasse, explique les fractions.', p); e.runAndWait(); print(p)"
python scripts/demo_voice_chat.py --file samples/speech.wav --host http://127.0.0.1:8010
```

Note: selon le moteur TTS actif, la réponse peut retourner des métadonnées audio temporaires (`audio_path` dans `/tmp`) sans URL persistante.

---

Fichier généré automatiquement par l'assistant — modifiez selon vos besoins.
