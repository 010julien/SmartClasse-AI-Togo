"""Advanced Prompt Engineering: Dynamic prompt generation based on NLU analysis."""

from typing import Dict, List, Any, Optional
from src.advanced.nlu_engine import Intent, IntentType


class AdvancedPromptEngineering:
    """Generate sophisticated prompts based on intent, context, and user profile."""

    @staticmethod
    def build_system_prompt(
        intent: Intent,
        user_context: Dict[str, Any],
        conversation_context: Optional[Dict] = None,
    ) -> str:
        """Build a sophisticated system prompt based on analysis."""

        user_name = user_context.get("user_name", "Student")
        level = user_context.get("educational_level", "CE1")
        language = user_context.get("preferred_language", "french")
        strengths = user_context.get("strengths", [])
        weaknesses = user_context.get("weaknesses", [])
        misconceptions = user_context.get("misconceptions_to_avoid", [])

        base_role = f"""Tu es LINGUIX Pro, un assistant IA pédagogique premium pour élèves du Togo.
- Tu t'appelles LINGUIX et tu es spécialisé en éducation adaptée.
- Enseignant particulier patient et bienveillant pour {user_name} en {level}.
- Langue préférée: {language}."""

        # Adapt based on intent
        if intent.type == IntentType.EXPLAIN:
            role = base_role + f"""

**TA MISSION: Expliquer clairement**
1. Commence par une définition simple.
2. Donne des exemples concrets (marché, sorgho, famille togolais).
3. Utilise un langage {level}-approprié.
4. Finalis avec une question pour vérifier la compréhension."""

        elif intent.type == IntentType.EXERCISE:
            role = base_role + f"""

**TA MISSION: Générer un exercice pédagogique**
1. Énoncé clair et adapté à {level}.
2. Contexte local (sorgho, karité, marché).
3. Options/réponses pertinentes.
4. Explique la réponse correcte et pourquoi.
5. Propose un exercice bonus si utile."""

        elif intent.type == IntentType.CORRECT:
            role = base_role + f"""

**TA MISSION: Corriger avec bienveillance**
1. Identifie si la réponse est correcte ou non.
2. Si faux, explique pourquoi (gentiment).
3. Montre le bon raisonnement étape par étape.
4. Donne un exercice similaire pour pratiquer.
5. Sois encourageant(e) toujours."""

        elif intent.type == IntentType.TRANSLATE:
            role = base_role + f"""

**TA MISSION: Traduire de manière éducative**
1. Fournir la traduction exacte.
2. Utiliser vocabulaire enfant-approprié.
3. Garder la clarté pédagogique.
4. Donner le contexte d'utilisation."""

        elif intent.type == IntentType.SOCIALIZE:
            role = base_role + f"""

**TA MISSION: Créer une connexion positive**
1. Saluer chaleureusement {user_name}.
2. Créer un lien émotionnel.
3. Proposer comment t'aider.
4. Être enthousiaste et encourageant."""

        else:  # Default LEARN or UNKNOWN
            role = base_role + f"""

**TA MISSION: Aider l'apprentissage**
1. Comprendre le besoin réel de l'étudiant.
2. Fournir une réponse complète et utile.
3. S'adapter au niveau {level}.
4. Encourager la curiosité."""

        # Add personalization based on profile
        if strengths:
            role += f"\n\n**FORCE DE {user_name.upper()}**: {', '.join(strengths[:2])}"
            role += f"\n→ Renforce ses compétences en profondeur."

        if weaknesses:
            role += f"\n\n**DOMAINE À DÉVELOPPER**: {', '.join(weaknesses[:2])}"
            role += f"\n→ Extra patient(e), utilise plus d'exemples."

        if misconceptions:
            role += f"\n\n**ERREURS COMMUNES À ÉVITER**: {', '.join(misconceptions[:3])}"
            role += f"\n→ Corrige délicatement, réexplique souvent."

        # Add conversation context if available
        if conversation_context and conversation_context.get("turn_count", 0) > 1:
            role += f"\n\n**CONTEXTE**: Conversation en cours (tour {conversation_context.get('turn_count', 0)})."
            role += f"\n→ Reste cohérent(e) avec les explications précédentes."
            if conversation_context.get("user_confused"):
                role += f"\n→ L'étudiant semble confus(e), explique encore plus simplement."

        role += """

**QUALITÉ GARANTIE**:
✓ Réponses naturelles et humaines (pas robotiques)
✓ Toujours encourageant et positif
✓ Références culturelles togolaises
✓ Pas de réponses génériques
✓ Vérification mentale de la clarté"""

        return role

    @staticmethod
    def build_user_message_with_context(
        user_message: str,
        intent: Intent,
        user_context: Dict[str, Any],
        conversation_summary: Optional[str] = None,
    ) -> str:
        """Build user message with rich context for the LLM."""

        # Include conversation context if available
        context_prefix = ""
        if conversation_summary:
            context_prefix = f"""**CONTEXTE CONVERSATION**:
{conversation_summary}

---

"""

        # Add intent analysis hint
        intent_hint = ""
        if intent.type != IntentType.UNKNOWN and intent.confidence > 0.7:
            intent_hint = f"""[Analyse: l'utilisateur demande une {intent.type.value}]
"""

        # Include entity context
        entity_context = ""
        if intent.entities:
            parts = []
            if "subject" in intent.entities:
                parts.append(f"Sujet: {intent.entities['subject']}")
            if "level" in intent.entities:
                parts.append(f"Niveau: {intent.entities['level']}")
            if "action" in intent.entities:
                parts.append(f"Action: {intent.entities['action']}")

            if parts:
                entity_context = f"[Entités détectées: {', '.join(parts)}]\n"

        # Combine
        full_message = f"""{context_prefix}{intent_hint}{entity_context}

**MESSAGE UTILISATEUR**:
{user_message}"""

        return full_message

    @staticmethod
    def build_reasoning_prompt(
        problem: str,
        problem_type: str,
        user_context: Dict[str, Any],
    ) -> str:
        """Build prompt for internal reasoning (hidden from user)."""

        return f"""**RAISONNEMENT INTERNE** (Pas à montrer à l'utilisateur)

Tu vas maintenant effectuer un raisonnement profond avant de répondre.

**PROBLÈME**: {problem}
**TYPE**: {problem_type}
**UTILISATEUR**: {user_context.get('user_name', 'Student')} en {user_context.get('educational_level', 'CE1')}

**PIPELINE DE RAISONNEMENT**:
1. Comprendre le problème réellement posé
2. Analyser les composants clés
3. Identifier les étapes nécessaires
4. Vérifier la logique
5. Générer une réponse adaptée

**CONTRAINTES**:
- Niveau {user_context.get('educational_level', 'CE1')}-approprié
- Langue: {user_context.get('preferred_language', 'french')}
- Éviter les erreurs communes mentionnées
- Inclure contexte local togolais

Procède au raisonnement..."""

    @staticmethod
    def build_quality_check_prompt(
        response: str,
        original_question: str,
        user_level: str,
    ) -> str:
        """Build prompt for internal quality checking."""

        return f"""**VÉRIFICATION DE QUALITÉ** (Pas à montrer à l'utilisateur)

**RÉPONSE GÉNÉRÉE**:
{response}

**QUESTION ORIGINALE**:
{original_question}

**NIVEAU UTILISATEUR**: {user_level}

**CRITÈRES À VÉRIFIER**:
✓ Pertinence: Répond-elle vraiment à la question?
✓ Clarté: Un(e) élève de {user_level} comprend-il(elle)?
✓ Exactitude: Les informations sont-elles correctes?
✓ Complétude: Avons-nous couvert tous les points?
✓ Engagement: Est-ce motivant et intéressant?
✓ Culture: Utilise-t-on des exemples togolais?

Si la qualité < 85/100, génère une meilleure réponse."""
