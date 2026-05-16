# SmartClasse AI Togo — Script de Démo Vidéo

**Durée cible : 2 min 30 sec**  
**Outil recommandé : OBS Studio (gratuit) ou l'enregistreur Windows (Win+G)**  
**Résolution : 1920x1080, 30fps minimum**

---

## Avant de tourner — Checklist

```powershell
# Terminal 1 — Démarrer Ollama
ollama serve

# Terminal 2 — Démarrer le backend
cd C:\Users\DELL\Desktop\SmartClasse-AI-Togo\SmartClasse-AI-Togo
.\venv\Scripts\Activate.ps1
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Vérifier que tout marche
Invoke-RestMethod http://localhost:8000/health
```

Fenêtres à avoir ouvertes :
- [ ] Terminal PowerShell avec le backend qui tourne
- [ ] Navigateur ouvert sur `http://localhost:8000/docs`
- [ ] VS Code avec le projet ouvert (optionnel, pour montrer le code)

---

## SCÈNE 1 — Accroche (0:00 → 0:20)

**À l'écran :** Fond noir ou slide simple avec le logo/titre

**Tu dis :**
> "3,2 millions d'enfants au Togo n'ont pas accès à une éducation de qualité.
> 60% des écoles rurales sont sans internet. Les classes font 80 élèves pour un seul enseignant.
> SmartClasse AI est un assistant pédagogique qui fonctionne entièrement hors-ligne,
> parle 6 langues dont l'Ewe et le Kabiyè, et suit le programme officiel togolais."

---

## SCÈNE 2 — Architecture rapide (0:20 → 0:35)

**À l'écran :** Ouvre le README.md dans VS Code — fais défiler jusqu'au schéma ASCII de l'architecture

**Tu dis :**
> "Le système est composé de 8 agents spécialisés : ADAPTIX génère les leçons,
> LINGUIX gère la voix et la traduction, DIAGNOSTIX analyse les progrès des élèves,
> et un ORCHESTRATEUR coordonne le tout. Tout tourne localement via Ollama avec Gemma 4."

---

## SCÈNE 3 — Backend en direct (0:35 → 0:55)

**À l'écran :** Navigateur sur `http://localhost:8000/docs`

**Tu dis :**
> "Voici l'API en direct. Le backend FastAPI expose tous les agents."

**Action :** Clique sur `GET /health` → Try it out → Execute

**Montre la réponse JSON :**
```json
{"status": "healthy", "agents": ["adaptix", "linguix", "diagnostix", ...]}
```

**Tu dis :**
> "Le système est opérationnel. Aucune connexion cloud — tout est local."

---

## SCÈNE 4 — ADAPTIX : Génération de leçon (0:55 → 1:20)

**À l'écran :** Swagger docs — `POST /agents/adaptix/generate`

**Clique sur Try it out, colle ce body :**
```json
{
  "student_name": "Mawuli",
  "level": "CE1",
  "subject": "Mathématiques",
  "topic": "Addition jusqu'à 20",
  "language": "french"
}
```

**Clique Execute — montre la réponse**

**Tu dis :**
> "ADAPTIX génère une leçon adaptée au niveau CE1, avec des exercices progressifs
> et des exemples culturellement proches de la réalité togolaise — le marché, l'agriculture,
> la vie du village. Tout ça en moins de 3 secondes, sans internet."

---

## SCÈNE 5 — LINGUIX : Chat multilingue (1:20 → 1:45)

**À l'écran :** `POST /agents/linguix/chat`

**Body :**
```json
{
  "message": "Explique-moi les fractions",
  "language": "french",
  "user_id": "mawuli_001",
  "user_name": "Mawuli",
  "user_level": "CE1"
}
```

**Execute — montre la réponse**

**Tu dis :**
> "LINGUIX gère le chat multilingue. Même requête en Ewe ou en Kabiyè —
> l'agent détecte la langue automatiquement et répond dans la même langue.
> Il supporte aussi la voix : envoi d'un audio, transcription avec Whisper,
> réponse vocale avec synthèse TTS — entièrement hors-ligne."

---

## SCÈNE 6 — DIAGNOSTIX : Analyse d'un élève (1:45 → 2:05)

**À l'écran :** `POST /agents/diagnostix/analyze`

**Body :**
```json
{
  "student_id": "mawuli_001",
  "student_name": "Mawuli",
  "level": "CE1",
  "language": "french"
}
```

**Execute — montre la réponse JSON avec strengths, gaps, risk_score**

**Tu dis :**
> "DIAGNOSTIX analyse le profil de l'élève : points forts, lacunes identifiées,
> score de risque de décrochage. Ces données alimentent le tableau de bord
> du professeur via PILOTIX — pour que l'enseignant sache exactement
> sur quels élèves concentrer son attention."

---

## SCÈNE 7 — Déploiement offline (2:05 → 2:20)

**À l'écran :** Montre le terminal — Ollama qui tourne localement

**Tu dis :**
> "Tout ce système tourne sur un Raspberry Pi 4 à 50 dollars.
> Pas de cloud. Pas d'abonnement. Pas de connexion.
> Un seul appareil peut servir toute une école.
> Les données des élèves ne quittent jamais le village."

---

## SCÈNE 8 — Outro (2:20 → 2:30)

**À l'écran :** Slide titre avec les tracks et le lien GitHub

```
SmartClasse AI Togo
github.com/010julien/SmartClasse-AI-Togo

Tracks : Ollama · Future of Education · Digital Equity
         Global Resilience · Cactus · Unsloth

Licence : CC-BY 4.0 + Apache 2.0
```

**Tu dis :**
> "SmartClasse AI — l'éducation personnalisée pour chaque enfant au Togo,
> même là où il n'y a pas d'électricité fiable et pas d'internet.
> Merci."

---

## Conseils d'enregistrement

| Conseil | Détail |
|---------|--------|
| Micro | Parle clairement, proche du micro — calme et posé |
| Vitesse | Ne va pas trop vite sur les réponses JSON — laisse 2s pour lire |
| Zoom | Dans OBS, tu peux zoomer sur la réponse JSON pour la rendre lisible |
| Erreur | Si une requête rate, coupe et recommence — ne laisse pas d'erreur à l'écran |
| Musique | Optionnel: musique de fond douce à -20dB |
| Format | Export MP4, H.264, 1080p |

## Après la vidéo

```
1. Upload sur YouTube (Unlisted ou Public)
2. Copie le lien
3. Ajoute dans README.md :
   [![Demo](https://img.youtube.com/vi/TON_ID/0.jpg)](https://youtube.com/watch?v=TON_ID)
4. Colle le lien dans le formulaire Kaggle (champ "Demo Video")
```
