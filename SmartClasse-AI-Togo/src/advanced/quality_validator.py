"""Quality Validator: Auto-evaluation and verification of responses before delivery."""

import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Dimensions of response quality."""
    RELEVANCE = "relevance"  # How relevant to the question
    ACCURACY = "accuracy"  # Factual correctness
    CLARITY = "clarity"  # How clear/understandable
    COMPLETENESS = "completeness"  # Does it answer fully
    APPROPRIATENESS = "appropriateness"  # Age/level appropriate
    GRAMMAR = "grammar"  # Grammar and spelling
    ENGAGEMENT = "engagement"  # How engaging/motivating


@dataclass
class QualityScore:
    """Quality assessment result."""
    overall_score: float  # 0-100
    scores_by_dimension: Dict[str, float]
    issues: List[str]  # Quality issues detected
    recommendations: List[str]  # Suggestions for improvement
    passes_threshold: bool  # Whether score >= 85
    needs_regeneration: bool


class QualityValidator:
    """Validates response quality before sending to user."""

    QUALITY_THRESHOLD = 75.0  # Seuil doctoral minimal pour réponses pédagogiques

    def __init__(self):
        self.dimension_weights = {
            QualityDimension.RELEVANCE: 0.25,
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.CLARITY: 0.15,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.APPROPRIATENESS: 0.10,
            QualityDimension.GRAMMAR: 0.10,
            QualityDimension.ENGAGEMENT: 0.05,
        }

    def validate(
        self,
        response: str,
        original_question: str,
        user_level: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> QualityScore:
        """Full quality validation pipeline."""

        scores = {}
        issues = []
        recommendations = []

        # 1. Relevance check
        relevance_score, rel_issues, rel_recs = self._check_relevance(response, original_question)
        scores[QualityDimension.RELEVANCE] = relevance_score
        issues.extend(rel_issues)
        recommendations.extend(rel_recs)

        # 2. Accuracy check (basic)
        accuracy_score, acc_issues, acc_recs = self._check_accuracy(response)
        scores[QualityDimension.ACCURACY] = accuracy_score
        issues.extend(acc_issues)
        recommendations.extend(acc_recs)

        # 3. Clarity check
        clarity_score, cla_issues, cla_recs = self._check_clarity(response)
        scores[QualityDimension.CLARITY] = clarity_score
        issues.extend(cla_issues)
        recommendations.extend(cla_recs)

        # 4. Completeness check
        completeness_score, com_issues, com_recs = self._check_completeness(response, original_question)
        scores[QualityDimension.COMPLETENESS] = completeness_score
        issues.extend(com_issues)
        recommendations.extend(com_recs)

        # 5. Age-appropriateness check
        appropriateness_score, app_issues, app_recs = self._check_appropriateness(response, user_level)
        scores[QualityDimension.APPROPRIATENESS] = appropriateness_score
        issues.extend(app_issues)
        recommendations.extend(app_recs)

        # 6. Grammar/spelling check
        grammar_score, gram_issues, gram_recs = self._check_grammar_spelling(response)
        scores[QualityDimension.GRAMMAR] = grammar_score
        issues.extend(gram_issues)
        recommendations.extend(gram_recs)

        # 7. Engagement check
        engagement_score, eng_issues, eng_recs = self._check_engagement(response)
        scores[QualityDimension.ENGAGEMENT] = engagement_score
        issues.extend(eng_issues)
        recommendations.extend(eng_recs)

        # Calculate weighted overall score
        overall_score = sum(
            scores.get(dim, 50) * self.dimension_weights[dim]
            for dim in self.dimension_weights
        )

        passes_threshold = overall_score >= self.QUALITY_THRESHOLD
        needs_regeneration = not passes_threshold

        logger.info(f"Quality validation: {overall_score:.1f} (passes={passes_threshold})")

        return QualityScore(
            overall_score=overall_score,
            scores_by_dimension={dim.value: scores.get(dim, 50) for dim in QualityDimension},
            issues=list(set(issues)),  # Deduplicate
            recommendations=list(set(recommendations)),
            passes_threshold=passes_threshold,
            needs_regeneration=needs_regeneration,
        )

    @staticmethod
    def _check_relevance(response: str, question: str) -> tuple:
        """Check if response is relevant to question."""
        issues = []
        recommendations = []
        score = 80.0  # Default

        # Check if response is too short or empty
        if len(response.strip()) < 20:
            score -= 30
            issues.append("Response too short")
            recommendations.append("Provide more detailed answer")

        # Basic keyword matching (rough relevance)
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words & response_words) / max(1, len(question_words))

        if overlap < 0.2:
            score -= 20
            issues.append("Response seems off-topic")
            recommendations.append("Ensure response addresses the question directly")
        elif overlap < 0.4:
            score -= 10
            issues.append("Response partially relevant")

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_accuracy(response: str) -> tuple:
        """Basic accuracy checks (detect obvious errors)."""
        issues = []
        recommendations = []
        score = 85.0  # Default

        # Check for logical contradictions
        if "contradict" in response.lower() or ("yes" in response.lower() and "no" in response.lower()):
            # Simple heuristic for contradictions
            if response.count("yes") > 0 and response.count("no") > 0 and len(response) < 200:
                score -= 20
                issues.append("Possible logical contradiction")
                recommendations.append("Verify statement is logically consistent")

        # Check for common hallucinations (placeholder patterns)
        if "[insert" in response.lower() or "todo" in response.lower() or "xxx" in response.lower():
            score -= 15
            issues.append("Incomplete/placeholder content")
            recommendations.append("Fill in all placeholders with real content")

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_clarity(response: str) -> tuple:
        """Check clarity and readability."""
        issues = []
        recommendations = []
        score = 85.0

        # Check average sentence length
        sentences = re.split(r'[.!?]+', response)
        avg_sentence_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))

        if avg_sentence_len > 30:
            score -= 15
            issues.append("Sentences too long and complex")
            recommendations.append("Break into shorter, simpler sentences")
        elif avg_sentence_len < 5:
            score -= 5
            issues.append("Sentences very short (maybe too fragmented)")

        # Check for jargon overload
        if len([w for w in response.split() if len(w) > 12]) > len(response.split()) * 0.2:
            score -= 10
            issues.append("Too much complex/specialized vocabulary")
            recommendations.append("Use simpler words where possible")

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_completeness(response: str, question: str) -> tuple:
        """Check if response is complete."""
        issues = []
        recommendations = []
        score = 85.0

        # Check for common incomplete patterns
        if response.endswith("..."):
            score -= 20
            issues.append("Response appears truncated")
            recommendations.append("Provide complete answer")

        if any(marker in response.lower() for marker in ["etc.", "and so on", "et caetera"]):
            score -= 10
            issues.append("Response uses non-specific endings")
            recommendations.append("Be more specific and complete")

        # Check response provides examples if asked
        if "example" in question.lower() and "example" not in response.lower():
            score -= 15
            issues.append("Question asked for examples but none provided")
            recommendations.append("Include at least one concrete example")

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_appropriateness(response: str, user_level: Optional[str] = None) -> tuple:
        """Check age-appropriateness."""
        issues = []
        recommendations = []
        score = 85.0

        # Check for adult content
        adult_words = ["adult", "mature", "sex", "violence", "death"]
        if any(word in response.lower() for word in adult_words):
            score -= 20
            issues.append("Potentially inappropriate content for children")
            recommendations.append("Rephrase to be age-appropriate")

        # Check vocabulary complexity for young learners
        if user_level in ["CE1", "CE2"]:
            complex_words = [w for w in response.split() if len(w) > 12]
            if len(complex_words) / max(1, len(response.split())) > 0.15:
                score -= 10
                issues.append(f"Too advanced for {user_level}")
                recommendations.append("Use simpler vocabulary for early grades")

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_grammar_spelling(response: str) -> tuple:
        """Check grammar and spelling (simple checks)."""
        issues = []
        recommendations = []
        score = 90.0

        # Check for multiple consecutive spaces
        if "  " in response:
            score -= 5
            issues.append("Extra spaces in text")

        # Check for obvious spelling errors (basic)
        common_typos = {"teh": "the", "recieve": "receive", "occured": "occurred"}
        for typo, correct in common_typos.items():
            if typo in response.lower():
                score -= 5
                issues.append(f"Possible spelling error: '{typo}'")
                recommendations.append(f"Check spelling (should be '{correct}')")
                break

        return min(100, max(0, score)), issues, recommendations

    @staticmethod
    def _check_engagement(response: str) -> tuple:
        """Check if response is engaging."""
        issues = []
        recommendations = []
        score = 80.0

        # Check for encouraging tone (FR + EN)
        encouraging_words = [
            # Français
            "bravo", "super", "excellent", "formidable", "bien joué",
            "félicitations", "magnifique", "très bien", "parfait", "génial",
            "courage", "continue", "bonne réponse", "intéressant",
            # English
            "great", "wonderful", "well done", "interesting",
            # Emojis courants
            "👏", "👍", "✨", "🎉", "😊", "💪",
        ]
        encouragement_count = sum(1 for word in encouraging_words if word in response.lower())

        if encouragement_count == 0:
            score -= 10  # Pénalité réduite
            issues.append("Response lacks encouraging tone")
            recommendations.append("Add positive reinforcement")

        # Check for questions (engagement)
        if "?" in response:
            score += 10  # Bonus for interaction
        else:
            score -= 5
            issues.append("No question to engage student")
            recommendations.append("Consider ending with a follow-up question")

        # Check for local context (cultural relevance) — accent-insensitive
        local_words = ["sorgho", "karite", "karité", "marche", "marché",
                       "togo", "togolais", "village", "école", "ecole",
                       "famille", "classe", "élève", "eleve", "enseignant"]
        if any(word in response.lower() for word in local_words):
            score += 10
        else:
            score -= 3  # Pénalité réduite
            issues.append("Could include more local/cultural context")
            recommendations.append("Reference familiar Togolese contexts")

        return min(100, max(0, score)), issues, recommendations
