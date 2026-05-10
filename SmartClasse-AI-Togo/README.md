# SmartClasse — Instructions de soumission Hackathon Gemma 4 Good

Ce dépôt contient le backend Python (FastAPI), agents LLM (Ollama / Gemma 4), et un client Flutter minimal.

Objectif rapide

- Stratégie : **Ollama‑first** (Gemma 4 local via Ollama) avec fallback edge **LiteRT / llama.cpp**.
- Licence gagnante requise : **CC‑BY 4.0** (préparer NOTICE et LICENSE).

Prérequis locaux

- Python 3.10+, virtualenv
- Node/Flutter pour le client (optionnel)
- Ollama (optionnel) — si disponible, expose une API locale sur `http://localhost:11434`
- (Fallback) LiteRT / llama.cpp — instructions ci‑dessous

Démarrage rapide (développement)

1. Créez et activez l'environnement Python :

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2. Démarrer le backend :

```powershell
.\scripts\start_backend.ps1
```

Ou manuellement:

```bash
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8010
```

3. Ouvrir le client Flutter (optionnel) :

```bash
cd flutter_client
flutter run -d chrome
```

Pour enchaîner les deux étapes dans le bon ordre:

```powershell
.\scripts\start_dev.ps1
```

Docker (backend)

```bash

docker build -t smartclasse-ai-togo .
docker run --rm -p 8000:8000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 smartclasse-ai-togo
```

Si l'image n'existe pas encore en local, exécutez d'abord `docker build -t smartclasse-ai-togo .`, puis relancez `docker run`.

Le point final `.` est le contexte de build. Sans lui, `docker build` renvoie l'erreur "requires 1 argument".

Sous Linux, ajoutez `--add-host=host.docker.internal:host-gateway` si le host Ollama doit être joint depuis le container.

Docker Compose (backend + Ollama)

```bash
docker compose up --build
```

Le backend sera disponible sur `http://localhost:8000` et Ollama sur `http://localhost:11434`.
Pour précharger le modèle Gemma 4 avant de lancer le backend, exécutez:

```bash
docker compose --profile setup run --rm ollama-pull
```

Le backend attend maintenant que le service Ollama soit sain avant de démarrer.

Ollama (Gemma 4) — recommandations

- Si vous disposez d'Ollama installé localement, démarrez son service/daemon selon la documentation Ollama.
- L'API attendue par le backend : `http://localhost:11434` (configurable via `src/config.py` ou variables d'environnement).

Fallbacks edge (LiteRT / llama.cpp)

- Préparez un binaire LiteRT/llama.cpp sur votre machine avec le modèle optimisé (consultez la doc des projets respectifs).
- Les scripts `scripts/start_fallback_*.sh` fournissent les commandes de base et l'emplacement attendu du modèle.

Packaging & soumission (Kaggle Hackathon)

- Une seule soumission par équipe — préparez votre version finale.
- Livrables minimaux :
  - code source complet
  - `requirements.txt`
  - `README.md` (ce fichier)
  - scripts de démarrage (`scripts/`)
  - `LICENSE` (CC-BY-4.0) + `NOTICE` si vous utilisez composants tiers
  - instructions reproductibles et Dockerfile optionnel

Scripts utiles

- `scripts/start_ollama.sh` / `.ps1` : vérifie la présence d'Ollama et affiche la commande recommandée.
- `scripts/start_backend.sh` / `.ps1` : démarre FastAPI sur `127.0.0.1:8010` et attend le endpoint `/health`.
- `scripts/start_dev.sh` / `.ps1` : démarre le backend puis affiche la commande Flutter à lancer.
- `scripts/start_fallback_llama_cpp.sh` : commande d'exemple pour lancer un serveur local llama.cpp/LiteRT.
- `scripts/package_submission.py` / `.sh` / `.ps1` : exécute les tests, vérifie la présence de `LICENSE` et `NOTICE`, puis crée `dist/smartclasse_submission_*.zip`.

Conformité des licences

- Vérifiez que tous les modèles/données externes utilisés sont redistribuables ou documentez leur provenance.
- Le code soumis doit être compatible avec CC‑BY 4.0 (inclure `LICENSE` et `NOTICE`).

Contact & équipe

### Checklist Kaggle finale

- [ ] Nom de l'équipe confirmé : [à compléter]
- [ ] Compte Kaggle de soumission validé : [à compléter]
- [ ] Rôle 1 attribué : [nom] - [rôle]
- [ ] Rôle 2 attribué : [nom] - [rôle]
- [ ] Rôle 3 attribué : [nom] - [rôle]
- [ ] Une seule soumission par équipe vérifiée
- [ ] `LICENSE` CC-BY 4.0 inclus
- [ ] `NOTICE` complété avec les composants tiers
- [ ] Archive de soumission générée et relue

Résumé équipe

- Chef de projet : [à compléter]
- Référent backend / IA : [à compléter]
- Référent frontend / intégration : [à compléter]
- Référent documentation / soumission : [à compléter]
- Compte Kaggle final : [à compléter]

---

Voir le dossier `scripts/` pour les fichiers de démarrage et d'automatisation.

# SmartClasse — Système Éducatif Adaptatif Souverain du Togo

[![Kaggle](https://img.shields.io/badge/Kaggle-Gemma%204%20Good%20Hackathon-blue)](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Offline First](https://img.shields.io/badge/Mode-Offline%20First-critical)](#architecture)
[![Languages](https://img.shields.io/badge/Languages-5%20Locales%20%2B%20Français-brightgreen)](#langues)

## 🎯 Le Problème en Une Phrase

Au Togo, un enseignant fait face à 78 élèves de 5 niveaux différents, dans une classe multilingue, sans aucun outil d'adaptation. SmartClasse résout cela avec **9 agents IA spécialisés**, déployés **offline sur une tablette Android à 80 euros**, en **langues locales**, propulsé par **Gemma 4**.

## 💡 La Solution

**SmartClasse** = 9 agents IA + Gemma 4 + Offline + 5 langues togolaises + 5 valeurs révolutionnaires

### 4 Agents Fondamentaux (Phase 1)

- **ADAPTIX** — Tuteur adaptatif personnel (exercices personnalisés)
- **DIAGNOSTIX** — Détecteur de lacunes précises
- **PILOTIX** — Premier tableau de bord enseignant
- **LINGUIX** — Pont linguistique en 5 langues locales + audio natif

### 5 Valeurs Révolutionnaires

- **KULTURIX** — Savoir oral des anciens intégré dans les leçons
- **RESEARCHIX** — Données pédagogiques africaines open source
- **PASSPORTIX** — Diplôme infalsifiable et vérifiable
- **EQUITIX** — Détection du décrochage silencieux des filles
- **PARENTIX** — SMS hebdomadaire parent en langue locale

## 🏗 Architecture Technique

```
EduPath AI
├── Gemma 4 E4B (3.9 GB, offline, 140+ langues)
├── LLM Chain (FastAPI)
├── RAG Local (Programme MEPS complet)
├── Audio Module (Whisper + Gemma 4 audio natif)
├── SQLite (Data chiffré AES-256)
├── SMS Gateway (GSM standard)
└── Interface Pictographique (non-lecteurs)
```

**Pourquoi Gemma 4 ?**
| Besoin | Gemma 4 | GPT-4 | Claude | Mistral |
|--------|---------|-------|--------|---------|
| Offline 100% | ✅ | ❌ Cloud | ❌ Cloud | ❌ |
| 5 langues locales | ✅ | ⚠️ Limité | ⚠️ Limité | ❌ |
| Multimodal audio offline | ✅ | ❌ | ❌ | ❌ |
| 9 agents autonomes | ✅ | ⚠️ | ⚠️ | ❌ |
| Apache 2.0 gratuit | ✅ | ❌ | ❌ | ⚠️ |
| Tablette 80€ | ✅ | ❌ | ❌ | ❌ |

## 📦 Installation Rapide

```bash
# 1. Clone repo
git clone https://github.com/[YourUsername]/EduPath-AI-Togo.git
cd EduPath-AI-Togo

# 2. Setup environnement
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download Gemma 4 E4B
ollama pull gemma4:e4b  # or from Hugging Face

# 5. Run API
python -m src.main
```

## 🚀 Demo

```bash
# Start local server
uvicorn src.main:app --reload --port 8000
Set-Location C:\Users\DELL\Desktop\SmartClasse-AI-Togo\SmartClasse-AI-Togo
.\venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000

# Test ADAPTIX (adaptation)
curl -X POST http://localhost:8000/agents/adaptix/generate \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "Kossi",
    "level": "CM1",
    "subject": "math",
    "topic": "fractions",
    "language": "kabyie"
  }'

# Test LINGUIX (audio multilingue)
curl -X POST http://localhost:8000/agents/linguix/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "instruction.wav",
    "source_language": "french",
    "target_languages": ["kabyie", "ewe", "haoussa"]
  }'
```

## 📊 Impact Chiffré (Togo 2025-2026)

| Métrique                        | Avant  | Après (Objectif 18 mois) |
| ------------------------------- | ------ | ------------------------ |
| Achèvement Savanes              | 23,6%  | 40%+                     |
| Redoublement                    | 20,2%  | 12%-                     |
| Filles en risque détectées      | 0%     | 95%+                     |
| Engagement parent               | 8% SMS | 85%+                     |
| Données pédagogiques africaines | 0      | 2M+ points               |

## 🎯 Phases de Déploiement

| Phase       | Cible                         | Élèves    | Délai    | KPI               |
| ----------- | ----------------------------- | --------- | -------- | ----------------- |
| **Phase 1** | Kpendjal (Savanes)            | 3,900     | 6 mois   | -15% redoublement |
| **Phase 2** | Savanes + Kara                | 280,000   | 18 mois  | PCT opérationnel  |
| **Phase 3** | National (primaire + collège) | 1,688,946 | 36 mois  | Standard national |
| **Phase 4** | Bénin, Ghana, Niger           | Multi-M   | 48+ mois | Standard régional |

## 📜 License

Apache 2.0 — Déploiement gratuit gouvernement + ONG

## 🤝 Partenaires

- **MEPS Togo** — Programme officiel
- **GPE (Partenariat Mondial Éducation)** — Pacte signé oct.2024
- **UNICEF Togo** — Scolarisation enfants défavorisés
- **ENFPE** — 5,125 élèves-professeurs en formation

## 📞 Contact & Support

**Projet** : Expert Innovation IA | Document Doctoral Légendaire — Édition Fusion  
**Date** : Mai 2026  
**Hackathon** : Kaggle Gemma 4 Good Challenge

---

**🌍 SmartClasse ne réinvente pas l'éducation. Il restitue à l'éducation togolaise ce qu'elle a toujours mérité : être à l'image de ceux qu'elle est censée former.**
