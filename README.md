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
