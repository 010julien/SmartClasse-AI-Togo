# SmartClasse Flutter Client

Client mobile Flutter pour discuter avec l'agent SmartClasse en:

- texte (`/agents/linguix/chat`)
- message vocal (`/agents/linguix/voice_pipeline`)
- contexte culturel local via KULTURIX (`/agents/kulturix/context`)

## Prerequis

- Flutter SDK installe
- Backend FastAPI SmartClasse en cours d'execution sur `:8010` via Docker Compose

### Lancer le backend avant Flutter

Sur Windows:

```powershell
..\scripts\start_backend.ps1
```

Ou enchaîner backend + rappel Flutter:

```powershell
..\scripts\start_dev.ps1
```

Sur macOS/Linux:

```bash
../scripts/start_backend.sh
```

## Installation

```bash
cd flutter_client
flutter pub get
```

## Lancer

```bash
cd flutter_client
flutter run -d chrome
```

Sur les versions récentes de Flutter, l'option `--web-renderer` n'est plus disponible. Le client SmartClasse est déjà configuré pour rester léger et fonctionner sans dépendances web distantes inutiles.

## Mode hors ligne

- Active le toggle `Mode hors ligne / démo` dans l'app pour tester sans backend.
- Les boutons `DIAGNOSTIX`, `PILOTIX`, `EQUITIX` et `PARENTIX` renvoient alors des exemples locaux.
- Le chat texte répond aussi avec un fallback local si le backend n'est pas joignable.

## Tests locaux

```bash
cd flutter_client
flutter test
```

```bash
cd ..
.\venv\Scripts\python.exe -m pytest tests\test_kulturix_offline.py -q
```

## Configuration URL API

L'app choisit automatiquement:

- Android emulator: `http://10.0.2.2:8010`
- iOS / desktop: `http://127.0.0.1:8010`

## Fonctionnalites

- Envoi message texte vers l'agent
- Reponse texte de l'agent
- Option TTS (lecture audio serveur)
- Enregistrement vocal local (WAV)
- Upload vocal vers pipeline et affichage transcription/reponse
- Mode web offline-friendly avec renderer HTML et police locale

## Endpoints utilises

- `POST /agents/linguix/chat`
- `POST /agents/linguix/voice_pipeline`
- `GET /agents/kulturix/context`
- `GET /audio/*` (lecture des fichiers audio generes)
