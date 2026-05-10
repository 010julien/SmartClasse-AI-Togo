# LINGUIX Premium: Architecture IA Conversationnelle Avancée

## 🎯 Vue d'ensemble

LINGUIX Premium est une transformation complète de votre agent IA en système conversationnel **comparable à ChatGPT/Gemini**, exploitant 100% des capacités de **Gemma 4**.

### Architecture Core

```
┌─────────────────────────────────────────────────────┐
│                  User Input                          │
└──────────────────────┬──────────────────────────────┘
                       │
                    ┌──▼──────────────────┐
                    │ PHASE 1: NLU Engine │
                    │ • Intent Detection  │
                    │ • Entity Extract.   │
                    │ • Context Analysis  │
                    └──────┬──────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ PHASE 2: Reasoning  │
                    │ • Chain-of-Thought  │
                    │ • Decomposition     │
                    │ • Multi-step CoT    │
                    └──────┬──────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ PHASE 3: Memory     │
                    │ • Short-term ctx    │
                    │ • User Profile      │
                    │ • Conversation hist │
                    └──────┬──────────────┘
                           │
         ┌─────────────────▼────────────────┐
         │ PHASE 4: Advanced Prompting      │
         │ • Dynamic system prompt          │
         │ • Context injection              │
         │ • User personalization           │
         └────────────┬────────────────────┘
                      │
         ┌────────────▼────────────────────┐
         │ PHASE 5: LLM Call (Gemma 4)    │
         │ • Sophisticated prompt           │
         │ • Full context window            │
         │ • Reasoning-enabled              │
         └────────────┬────────────────────┘
                      │
         ┌────────────▼────────────────────┐
         │ PHASE 6: Quality Validation     │
         │ • Relevance check                │
         │ • Clarity assessment             │
         │ • Age-appropriateness            │
         │ • Auto-regeneration if needed    │
         └────────────┬────────────────────┘
                      │
         ┌────────────▼────────────────────┐
         │ PHASE 7: Memory Update          │
         │ • Save conversation             │
         │ • Update user profile           │
         │ • Track progress                │
         └────────────┬────────────────────┘
                      │
                 ┌────▼────────┐
                 │  Final      │
                 │  Response   │
                 └─────────────┘
```

---

## 🧠 Module 1: NLU Engine (Natural Language Understanding)

### Capacités

- **Intent Detection**: Classifie automatiquement l'intention (EXPLAIN, EXERCISE, CORRECT, TRANSLATE, etc.)
- **Entity Extraction**: Détecte sujet, niveau d'étude, langue, action spécifique
- **Context Analysis**: Analyse l'historique conversationnel pour détecter confusion, répétitions

### Code d'utilisation

```python
from src.advanced.nlu_engine import NLUEngine

engine = NLUEngine()
result = engine.analyze(
    "Je suis en CE1 et je veux une explication sur les fractions",
    messages=[...]  # optional history
)

# Résultat
print(result["intent"].type)          # IntentType.EXPLAIN
print(result["entities"]["level"])    # "CE1"
print(result["entities"]["subject"])  # "math"
print(result["analysis_confidence"])  # 0.92
```

---

## 🔄 Module 2: Reasoning Engine (Chain-of-Thought)

### Stratégies de raisonnement

- **Math Reasoning**: Identification → Décomposition → Application → Vérification
- **Explanation Reasoning**: Concept → Niveau → Contexte local → Structure logique
- **Exercise Generation**: Objectif → Progression → Contexte → Feedback
- **Correction**: Analyse → Comparaison → Diagnostic → Correction ciblée

### Code d'utilisation

```python
from src.advanced.reasoning_engine import ReasoningEngine

engine = ReasoningEngine()
chain = engine.reason(
    problem="Explique les fractions",
    problem_type="explanation",
    context={"educational_level": "CE1"}
)

# Résultat: chain complète avec étapes
for step in chain.steps:
    print(f"Step {step.step_number}: {step.description}")
    print(f"  Analysis: {step.analysis}")
    print(f"  Confidence: {step.confidence}")

print(f"Final Conclusion: {chain.final_conclusion}")
print(f"Total reasoning time: {chain.total_reasoning_time_ms}ms")
```

---

## 💾 Module 3: Memory Manager (Court & Long Terme)

### Conversation Memory (Court Terme)

```python
from src.advanced.memory_manager import MemoryManager

manager = MemoryManager()

# Initialiser session
session = manager.initialize_session(
    session_id="sess_123",
    user_id="user_001",
    user_name="Kossi"
)

# Ajouter une interaction
manager.add_turn(
    session_id="sess_123",
    user_id="user_001",
    user_message="Explique les fractions",
    assistant_message="Une fraction est..."
)

# Récupérer contexte pour prochaine réponse
context = manager.get_context_for_response("sess_123", "user_001")
print(context["conversation"]["recent_messages"])
print(context["conversation_summary"])
```

### User Profile (Long Terme)

```python
# Récupérer profil utilisateur
profile = manager.user_profiles.get_profile("user_001")

# Ajouter découvertes pédagogiques
manager.user_profiles.add_strength("user_001", "verbal_reasoning")
manager.user_profiles.add_weakness("user_001", "fraction_concepts")
manager.user_profiles.add_misconception("user_001", "fraction_larger_than_whole")

# Mettre à jour interaction
manager.user_profiles.record_interaction(
    "user_001",
    subject="math",
    interaction_type="exercise",
    success=True
)
```

---

## ✅ Module 4: Quality Validator (Auto-Évaluation)

### Dimensions de qualité évaluées

1. **Relevance** (25%): La réponse répond-elle vraiment?
2. **Accuracy** (20%): Les informations sont-elles correctes?
3. **Clarity** (15%): Est-ce compréhensible pour le niveau?
4. **Completeness** (15%): Couvre-t-on tous les points?
5. **Appropriateness** (10%): Adapté à l'âge/niveau?
6. **Grammar** (10%): Orthographe et grammaire correctes?
7. **Engagement** (5%): Motivant et intéressant?

### Utilisation

```python
from src.advanced.quality_validator import QualityValidator

validator = QualityValidator()
score = validator.validate(
    response="Une fraction représente une partie...",
    original_question="Qu'est-ce qu'une fraction?",
    user_level="CE1"
)

print(f"Overall Score: {score.overall_score}/100")
print(f"Passes Threshold (85): {score.passes_threshold}")
print(f"Issues found: {score.issues}")
print(f"Recommendations: {score.recommendations}")

if not score.passes_threshold:
    # Déclencher régénération automatique
    regenerated_response = regenerate_response(...)
```

---

## 🎨 Module 5: Advanced Prompt Engineering

### Dynamic System Prompts par Intent

```python
from src.advanced.prompts import AdvancedPromptEngineering

prompt = AdvancedPromptEngineering.build_system_prompt(
    intent=nlu_result["intent"],
    user_context={
        "user_name": "Kossi",
        "educational_level": "CE1",
        "preferred_language": "french",
        "strengths": ["verbal_reasoning"],
        "weaknesses": ["fractions"],
        "misconceptions_to_avoid": ["fraction_larger_than_whole"]
    },
    conversation_context=memory_context
)

# Prompt généré est hautement contextualisé et personnalisé
print(prompt)  # "Tu es LINGUIX Pro, expert pédagogue...
               # Tuteur particulier pour Kossi en CE1..."
```

---

## 🔗 Module 6: Conversation Manager (Orchestration)

### Pipeline Complet

```python
from src.advanced.conversation_manager import ConversationManager

manager = ConversationManager()

# Process une conversation complète
response = manager.process_conversation(
    session_id="sess_123",
    user_id="user_001",
    user_name="Kossi",
    messages=[
        {"role": "user", "content": "Bonjour, explique les fractions"},
        {"role": "assistant", "content": "Bonjour Kossi!..."},
        {"role": "user", "content": "Plus simple encore"}
    ],
    language="french",
    user_level="CE1",
    max_retries_on_quality=2  # Retry si qualité < 85
)

# Résultat complet
print(f"Message: {response.message}")
print(f"Intent: {response.intent} (confidence: {response.confidence})")
print(f"Quality Score: {response.quality_score}/100")
print(f"Used regeneration: {response.used_regeneration}")
print(f"Total time: {response.total_time_ms}ms")
```

---

## 🚀 Intégration dans FastAPI

### Endpoint LINGUIX Premium

```python
@app.post("/agents/linguix/chat")
async def linguix_chat(request: dict):
    """
    Premium chat avec personnalisation complète.
    
    Body:
    {
        "messages": [{"role":"user", "content":"..."}],
        "language": "french",
        "user_level": "CE1",
        "user_id": "user_001",
        "user_name": "Kossi",
        "speak": false
    }
    """
    result = await run_in_threadpool(
        linguix.chat,
        request["messages"],
        request.get("speak", False),
        request.get("language", "french"),
        request.get("user_level", "CE1"),
        request.get("user_id"),
        request.get("user_name", "Student")
    )
    return {"status": "success", "result": result}
```

### Utilisation depuis Flutter

```dart
final response = await http.post(
  Uri.parse('$baseUrl/agents/linguix/chat'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'messages': messages,
    'language': 'french',
    'user_level': 'CE1',
    'user_id': studentId,
    'user_name': 'Kossi',
    'speak': true,
  }),
);

final result = json.decode(response.body)['result'];
print(result['assistant_text']);  // Réponse premium
print(result['quality_score']);   // 95.3
print(result['intent']);          // 'explain'
```

---

## 📊 KPI et Métriques

### Performance Attendues

| Métrique | Target | Résultat |
|----------|--------|----------|
| Intent Accuracy | > 95% | Détection CoT |
| Quality Score Moyen | > 90/100 | Auto-validation |
| Avg Response Time | < 3s | Reasoning + LLM |
| User Satisfaction | > 95% | ChatGPT-like |
| Hallucination Rate | < 5% | Validation stricte |

### Logs et Debugging

```python
logger.info(f"NLU: Intent={intent.type.value} Conf={intent.confidence:.2f}")
logger.info(f"Reasoning: Steps={len(chain.steps)} Time={chain.total_reasoning_time_ms}ms")
logger.info(f"Memory: SessionTurns={session_turn_count} UserHistory={len(user_profile.subjects_history)}")
logger.info(f"Quality: Score={quality_score:.1f} Passes={passes_threshold}")
logger.info(f"Total: {total_time_ms}ms (NLU: {nlu_time}ms + Reasoning: {reasoning_time}ms + LLM: {llm_time}ms)")
```

---

## 🎓 Cas d'Usage

### Exemple 1: Explication pédagogique

**User**: "Je suis en CE1 et j'ai pas compris les fractions"

**Pipeline**:
1. **NLU**: Intent=EXPLAIN, Level=CE1, Subject=math
2. **Reasoning**: 4 étapes → Adapter niveau → Contexte local → Structure logique
3. **Memory**: Charge préférences CE1, ajoute "fractions" aux intérêts
4. **Prompt**: Système très précis: "Tuteur pour Kossi en CE1 sur fractions..."
5. **LLM**: Gemma 4 génère explications ultra-claires
6. **Quality**: 96/100 ✓ Pertinence + Clarté + Contexte
7. **Response**: "Une fraction représente une partie d'un tout. Imagine 8 sacs de sorgho..."

### Exemple 2: Génération d'exercice

**User**: "Donne-moi un exercice"

**Pipeline**:
1. **NLU**: Intent=EXERCISE, Context=conversation précédente
2. **Reasoning**: Génération progressive → Contexte togolais → Feedback
3. **Memory**: Récupère que l'élève maîtrise fractions basiques
4. **Prompt**: "Génère exercice CE1 fractions progressif, contexte marché/sorgho"
5. **LLM**: Créé exercice pertinent et progressif
6. **Quality**: 94/100 ✓ Pertinence + Progression
7. **Response**: Énoncé + 4 options + explication

---

## 🔧 Configuration & Tuning

### Gemma 4 Optimization

```python
# Dans config.py
LLM_TEMPERATURE = 0.3  # Stabilité pour pédagogie
LLM_MAX_TOKENS = 1024  # Réponses complètes mais concises
LLM_CONTEXT_WINDOW = 8192  # Full context support

# Dans conversation_manager
max_retries_on_quality = 2  # Régénération si qualité < 85
```

### Ajustement des seuils de qualité

```python
# Dans quality_validator.py
QUALITY_THRESHOLD = 85.0  # Elever pour être plus strict
dimension_weights = {
    RELEVANCE: 0.25,  # Critique pour pédagogie
    ACCURACY: 0.20,   # Pas d'erreurs factuelles
    CLARITY: 0.15,    # Pour jeunes élèves
    APPROPRIATENESS: 0.10,  # Age-approprié
    # ...
}
```

---

## 🧪 Tests

```bash
# Tester les modules avancés
python -m pytest tests/test_premium_linguix.py -v

# Exemples:
# ✓ test_nlu_engine.py
# ✓ test_reasoning_engine.py  
# ✓ test_memory_manager.py
# ✓ test_quality_validator.py
# ✓ test_conversation_manager.py
```

---

## 📈 Roadmap Futur

- [ ] Multi-language reasoning (kabyie, ewe, haoussa)
- [ ] Long-term learning: Student growth tracking
- [ ] Teacher dashboard: Class analytics
- [ ] Voice-to-voice conversations with premium TTS
- [ ] Offline reasoning cache: Pre-computed reasoning chains
- [ ] Advanced diagnostics: Adaptive testing engine
- [ ] Curriculum alignment: Standards-based recommendations

---

## ✨ Résumé

LINGUIX Premium transforme votre agent en **assistant conversationnel premium**:

✅ **NLU Avancé**: Comprend intentions complexes + contexte  
✅ **Reasoning CoT**: Pense avant de répondre  
✅ **Memory System**: Contexte + Profil utilisateur  
✅ **Quality Control**: Auto-validation + régénération  
✅ **Personalization**: Niveau + langue + préférences  
✅ **Performance**: Optimisation Gemma 4 complète  

**Résultat**: Conversations comparables à **ChatGPT/Gemini**, 100% offline-capable. 🚀
