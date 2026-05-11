# SmartClasse AI Togo

Backend FastAPI + agents educatifs (ADAPTIX, LINGUIX, etc.) avec execution locale Ollama (Gemma 4) et client Flutter.

## Etat actuel valide

- Backend Docker Compose demarre correctement sur `http://127.0.0.1:8010`
- Ollama disponible sur `http://127.0.0.1:11434`
- Endpoint sante: `GET /health`
- Chat texte: `POST /agents/linguix/chat`
- Chat voix (multipart): `POST /agents/linguix/chat` avec `file`
- Pipeline voix traduction: `POST /agents/linguix/voice_pipeline`
- Audio statique: `GET /audio/*`

## Prerequis

- Docker Desktop
- Python 3.10+
- (Optionnel) Flutter SDK pour le client web/mobile

## Demarrage rapide (recommande)

```powershell
docker compose up --build -d
Invoke-RestMethod http://127.0.0.1:8010/health
```

## Build backend allege (Ollama-first)

Le `Dockerfile` accepte un argument `REQUIREMENTS`.

```powershell
docker compose build backend --no-cache --build-arg REQUIREMENTS=requirements.ollama.txt
docker compose up -d --force-recreate backend
```

## Endpoints utiles

- `GET /health`
- `POST /agents/linguix/chat`
- `POST /agents/linguix/transcribe`
- `POST /agents/linguix/voice_pipeline`
- `POST /agents/linguix/tts_stream`
- `GET /docs`

## Exemples API

### Chat texte

```powershell
$body = @{
  messages = @(@{ role = "user"; content = "Bonjour, explique les fractions" })
  speak = $false
  language = "french"
  user_level = "CE1"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://127.0.0.1:8010/agents/linguix/chat -Method Post -ContentType "application/json" -Body $body
```

### Chat voix (multipart)

```powershell
$form = @{
  file = Get-Item ".\\samples\\speech.wav"
  language = "french"
  speak = "true"
  user_id = "demo_user"
  user_name = "Demo"
}

Invoke-RestMethod -Uri http://127.0.0.1:8010/agents/linguix/chat -Method Post -Form $form
```

## Scripts utiles

- `scripts/start_backend.ps1` / `.sh`
- `scripts/start_dev.ps1` / `.sh`
- `scripts/demo_voice_chat.py`
- `scripts/gen_sample.py`
- `scripts/benchmark_linguix_latency.py`
- `scripts/package_submission.py`

## Benchmark rapide

```powershell
python scripts\benchmark_linguix_latency.py --iterations 10 --mode both
```

Ce benchmark utilise des stubs legers pour mesurer le cout Python du pipeline.

## Client Flutter

```bash
cd flutter_client
flutter pub get
flutter run -d chrome
```

Voir aussi `flutter_client/README.md`.

## Notes

- Le TTS est resilient: si le moteur natif n'est pas disponible, l'API ne doit pas planter.
- Les metadonnees audio peuvent pointer vers un chemin temporaire selon le moteur TTS actif.
- Pour un run demo robuste, privilegier l'endpoint statique `/audio/*` quand `audio_url` est present.

## Licence

Le repository contient `LICENSE` et `NOTICE.txt` a conserver pour la soumission.
