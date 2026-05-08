# 📅 ROADMAP — 10 Days to Kaggle Gemma 4 Victory

## Timeline Critique

```
Jour 1  (8 mai)  → Inscription + Repo + Architecture
Jour 2-3 (9-10)  → ADAPTIX + LINGUIX prototypes + tests
Jour 4-5 (11-12) → DIAGNOSTIX + PILOTIX + intégration MEPS
Jour 6-7 (13-14) → Corpus culturel (KULTURIX) + SMS (PARENTIX)
Jour 8   (15)    → Polish code + optimisation Gemma 4
Jour 9   (16)    → Vidéo démo 3 min
Jour 10  (17)    → Rapport Kaggle + soumission finale (deadline 18 mai)
```

---

## 📌 JOUR 1 — FAIT (8 mai)

### ✅ Complété

- [x] Inscription Kaggle
- [x] Création repo GitHub "EduPath-AI-Togo"
- [x] Architecture complète (README + SETUP + QUICK_START)
- [x] Prototypes ADAPTIX (gen exercices) + LINGUIX (multilingue audio)
- [x] Structure FastAPI prête
- [x] Licence Apache 2.0

### ⏳ À Faire (3-4h)

1. Push repository sur GitHub
2. Télécharger Gemma 4 E4B via Ollama (~30 min download)
3. Installer Python + dependencies (~10 min)
4. Lancer API locale et tester santé check
5. Tester ADAPTIX endpoint
6. Tester LINGUIX endpoint

### 📊 Progress: 70% (repo + agents prêts, setup local reste)

---

## 📌 JOUR 2-3 — ADAPTIX + LINGUIX COMPLETS (9-10 mai)

### Objectifs Jour 2

- [x] Intégrer Gemma 4 E4B réel dans ADAPTIX
- [ ] Charger programme MEPS complet (JSON)
- [ ] Générer exercices réelles testées
- [ ] Créer profil élève avec diagnostic (5 exercices)

### Objectifs Jour 3

- [ ] Intégrer Whisper pour transcription audio
- [ ] Tester traduction multilingue (kabyie, ewe, haoussa)
- [ ] Générer audio pour chaque traduction
- [ ] Créer démo : "Instruction en français → Audio en 3 langues"

### Code Changes

```python
# adaptix.py: Replace _call_gemma4() mock with real Ollama call
# linguix.py: Replace _translate_via_gemma4() mock with real call
# linguix.py: Implement _generate_audio() with TTS offline
```

### Testing Points

```
POST /agents/adaptix/generate → Returns real exercise
POST /agents/linguix/translate_instruction → Returns translations + audio
```

### 📊 Output: 2 agents complets + tests passants

---

## 📌 JOUR 4-5 — DIAGNOSTIX + PILOTIX (11-12 mai)

### DIAGNOSTIX (Jour 4)

```
Input: Élève échoue à CM1 exercise
Output: "Lacune: tables 7-8 (CE2 prérequis)"
        "Cause: dénombrement par groupes (CP1 manquant)"
```

**Implementation**

- Model prerequisite graph (CE1 → CE2 → CM1)
- Reverse trace from failure
- Identify exact gap

### PILOTIX (Jour 5)

```
Teacher Dashboard for Kofi:
- 78 élèves vue global
- Top 5 in difficulty
- Suggested exercises today
- SMS notifications (PARENTIX)
```

**Implementation**

- Query student profiles
- Aggregate metrics
- Generate daily suggestions

### 📊 Output: 4 core agents opérationnels

---

## 📌 JOUR 6-7 — KULTURIX + PARENTIX (13-14 mai)

### KULTURIX (Jour 6) — Cultural Wisdom Integration

```
Corpus local → Every exercise context
"Sorghum", "karité", "marché", "grenier"
```

**Implementation**

- Load cultural JSON
- Inject references in ADAPTIX generation
- Validate with real examples

### PARENTIX (Jour 7) — SMS Parents

```
Every Friday 18:00:
"[EduPath] Kossi progresse en maths (+2 niveaux).
 Aide-le en fractions. Message gratuit."
```

**Implementation** (simulation only, SMS requires API key)

- Format SMS templates
- Translate to 5 languages
- Log SMS queue

### 📊 Output: 6 agents + 1 integration layer

---

## 📌 JOUR 8 — POLISH & OPTIMIZE (15 mai)

### Code Quality

- [ ] Refactor duplications
- [ ] Add proper error handling
- [ ] Optimize Gemma 4 prompts
- [ ] Add logging/monitoring

### Performance

- [ ] Benchmark response times
- [ ] Reduce latency (< 2s per request)
- [ ] Optimize audio generation

### Documentation

- [ ] Update README with real results
- [ ] Create API documentation
- [ ] Add deployment guide

### 📊 Output: Production-ready code

---

## 📌 JOUR 9 — VIDEO DEMO 3 MIN (16 mai)

### Script

```
0:00-0:20   Accroche: Kossi, pizza, fractions, Afissa
0:20-0:45   Problem: 23.6%, 46% unemployment, 0.7 girl ratio
0:45-1:35   DEMO LIVE
            → ADAPTIX generating sorghum exercise
            → LINGUIX translating to Kabyie audio
            → DIAGNOSTIX showing gap
            → EQUITIX showing Afissa risk
            → SMS parent in Kabyie
            → PCT showing 6 skills
1:35-2:05   9 Agents explanation
2:05-2:40   Impact: 2.8M students, GPE partnership
2:40-3:00   Conclusion: "Restituer l'éducation à l'éducation togolaise"
```

### Filming

- Clean desktop
- Terminal + FastAPI responses visible
- Call /agents/ endpoints live
- Show JSON outputs
- Beautiful transitions

### 📊 Output: YouTube video (public, unlisted)

---

## 📌 JOUR 10 — RAPPORT KAGGLE + SUBMISSION (17 mai, deadline 18 mai 23:59 UTC)

### Rapport Kaggle (1500 words max)

```
Title: "EduPath AI: Offline Adaptive Education for Togo"
Subtitle: "9 IA Agents + Gemma 4 + 5 Local Languages + 0 Internet"

Structure:
1. Problem Statement (200 words)
   - Togo education crisis with data
   - Kossi, Afissa, Frédéric stories

2. Solution Overview (300 words)
   - 9 agents + 5 values
   - Gemma 4 offline justification
   - Architecture diagram

3. Technical Implementation (400 words)
   - ADAPTIX + LINGUIX prototypes
   - Gemma 4 E4B integration
   - llama.cpp or Ollama choice
   - Real code snippets

4. Results & Testing (300 words)
   - Agent test results
   - Performance metrics
   - User feedback (if any)

5. Impact Potential (300 words)
   - Phase 1-4 timeline
   - 2.8M students target
   - GPE partnership confirmed

6. Code Quality (100 words)
   - Apache 2.0 license
   - GitHub repo link
   - Reproducibility proof
```

### Attachments

1. **Video** — 3 min demo (YouTube link)
2. **GitHub** — Full source code (public repo)
3. **Demo** — Live API (Hugging Face Spaces or local link)
4. **Gallery** — Screenshots of agents + outputs

### Submission Checklist

- [ ] Video uploaded to YouTube (unlisted)
- [ ] GitHub repo public + README complete
- [ ] All code properly documented
- [ ] LICENSE file = Apache 2.0
- [ ] Kaggle report written (< 1500 words)
- [ ] Cover image created
- [ ] Demo link working
- [ ] All links tested
- [ ] Submitted before 18 may 23:59 UTC

### 📊 Output: SUBMITTED ✅

---

## 🎯 Success Metrics

| Metric                  | Target      | Reality (est.)               |
| ----------------------- | ----------- | ---------------------------- |
| Impact Score (40pts)    | 35+         | Story: Kossi + Afissa + data |
| Video Quality (30pts)   | 25+         | Live demo WOW factor         |
| Technical Depth (30pts) | 25+         | Real agents + Gemma 4 proof  |
| **TOTAL**               | **90+/100** | **→ Top 1-3 worldwide**      |

---

## 🚨 Critical Success Factors

1. **Gemma 4 Real Integration** — Not mocked, actual LLM calls
2. **Live Audio Demo** — Kabiyè translation + audio in video
3. **Story > Code** — Jury wants impact narrative (Kossi + Afissa)
4. **Technical Proof** — Code on GitHub validates everything
5. **Timing** — Submit EARLY (day 9, not day 10)

---

## 📱 Daily Standup Template

```
Day X — [Status]

✅ DONE:
- Task 1
- Task 2

⏳ IN PROGRESS:
- Task 3

🚧 BLOCKED:
- Task 4 (waiting for...)

📊 PROGRESS: X%
```

---

**Goal**: Win Main Prize ($50K) + Impact Track ($10K education) = $60K  
**Deadline**: May 18, 2026 — 23:59 UTC  
**Submission**: Day 9 (buffer for last-minute fixes)
