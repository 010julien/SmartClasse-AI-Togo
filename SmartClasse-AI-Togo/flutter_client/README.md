# SmartClasse Flutter Client

Client Flutter pour interagir avec le backend SmartClasse:

- chat texte
- message vocal (upload)
- lecture audio serveur (`/audio/*`)
- contexte culturel (`/agents/kulturix/context`)

## Prerequis

- Flutter SDK
- Backend SmartClasse actif sur `http://127.0.0.1:8010`

## Lancer le backend avant Flutter

Depuis le dossier du projet backend:

```powershell
docker compose up --build -d
Invoke-RestMethod http://127.0.0.1:8010/health
```

Alternative scripts:

```powershell
..\scripts\start_backend.ps1
```

## Installation Flutter

```bash
cd flutter_client
flutter pub get
```

## Execution

```bash
cd flutter_client
flutter run -d chrome
```

## Configuration API

L'application selectionne automatiquement l'URL selon la plateforme:

- Android emulator: `http://10.0.2.2:8010`
- iOS / desktop: `http://127.0.0.1:8010`

## Endpoints utilises

- `POST /agents/linguix/chat`
- `POST /agents/linguix/voice_pipeline`
- `GET /agents/kulturix/context`
- `GET /audio/*`

## Notes voix

- Pour envoyer un audio, l'app effectue un upload multipart.
- Cote backend, la route `POST /agents/linguix/chat` accepte aussi un `file` pour le mode vocal.
- En cas d'absence de voix detectee, le backend peut retourner une reponse informative sans audio.

## Mode hors ligne

- Active le toggle mode hors ligne/demo pour tester sans backend.
- Certaines fonctions renvoient des exemples locaux si l'API est indisponible.

## Tests

```bash
cd flutter_client
flutter test
```
