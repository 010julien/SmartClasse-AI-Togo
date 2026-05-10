"""Reasoning Engine: Deep reasoning with Chain-of-Thought and problem decomposition."""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """Single reasoning step in a chain."""
    step_number: int
    description: str
    analysis: str
    sub_conclusions: List[str]
    confidence: float


@dataclass
class ReasoningChain:
    """Full reasoning chain for a problem."""
    problem: str
    problem_type: str  # e.g., "math_fraction", "explanation", "exercise_generation"
    steps: List[ReasoningStep]
    final_conclusion: str
    reasoning_confidence: float
    total_reasoning_time_ms: float


class ReasoningEngine:
    """Deep Reasoning Engine using Chain-of-Thought strategy."""

    def __init__(self):
        self.reasoning_strategies = {
            "math": self._reason_math,
            "explanation": self._reason_explanation,
            "exercise_generation": self._reason_exercise,
            "correction": self._reason_correction,
            "translation": self._reason_translation,
        }

    def reason(self, problem: str, problem_type: str = "explanation", context: Optional[Dict] = None) -> ReasoningChain:
        """Execute reasoning chain for a problem.

        Args:
            problem: The problem/query to reason about
            problem_type: Type of reasoning (math, explanation, etc.)
            context: Additional context (student level, subject, etc.)

        Returns:
            ReasoningChain with step-by-step reasoning
        """
        import time
        start_time = time.time()

        strategy = self.reasoning_strategies.get(problem_type, self._reason_explanation)
        steps = strategy(problem, context or {})

        # Aggregate sub-conclusions into final conclusion
        final_conclusion = self._aggregate_conclusions(steps, problem)

        # Calculate overall confidence
        avg_confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.5

        elapsed_ms = (time.time() - start_time) * 1000

        return ReasoningChain(
            problem=problem,
            problem_type=problem_type,
            steps=steps,
            final_conclusion=final_conclusion,
            reasoning_confidence=avg_confidence,
            total_reasoning_time_ms=elapsed_ms,
        )

    def _reason_math(self, problem: str, context: Dict) -> List[ReasoningStep]:
        """Reasoning for math problems."""
        steps = []

        # Step 1: Identify the problem type
        steps.append(ReasoningStep(
            step_number=1,
            description="Identify Problem Type",
            analysis="Analyze the mathematical operation: fraction, geometry, algebra, etc.",
            sub_conclusions=["Determine base operation needed"],
            confidence=0.9,
        ))

        # Step 2: Break down the problem
        steps.append(ReasoningStep(
            step_number=2,
            description="Decompose Problem",
            analysis="Break into simpler sub-problems that can be solved sequentially.",
            sub_conclusions=["Identify prerequisites", "Order steps logically"],
            confidence=0.85,
        ))

        # Step 3: Apply reasoning
        steps.append(ReasoningStep(
            step_number=3,
            description="Apply Mathematical Reasoning",
            analysis="Use appropriate mathematical rules and formulas.",
            sub_conclusions=["Apply formula", "Calculate intermediate results"],
            confidence=0.8,
        ))

        # Step 4: Verify
        steps.append(ReasoningStep(
            step_number=4,
            description="Verify Solution",
            analysis="Check answer using alternative methods or reverse calculation.",
            sub_conclusions=["Cross-check result", "Ensure units/format correct"],
            confidence=0.85,
        ))

        return steps

    def _reason_explanation(self, problem: str, context: Dict) -> List[ReasoningStep]:
        """Reasoning for explanations."""
        steps = []

        # Step 1: Understand the concept
        steps.append(ReasoningStep(
            step_number=1,
            description="Understand Core Concept",
            analysis="Identify the fundamental concept or principle to explain.",
            sub_conclusions=["Define key terms", "Identify prerequisites"],
            confidence=0.9,
        ))

        # Step 2: Identify appropriate level
        level = context.get("educational_level", "CE1")
        steps.append(ReasoningStep(
            step_number=2,
            description=f"Adapt to Level {level}",
            analysis=f"Tailor explanation complexity and vocabulary for {level} students.",
            sub_conclusions=["Use age-appropriate vocabulary", "Avoid advanced concepts"],
            confidence=0.85,
        ))

        # Step 3: Find real-world context
        steps.append(ReasoningStep(
            step_number=3,
            description="Find Cultural/Local Context",
            analysis="Connect to students' daily life: sorghum, shea, market scenarios.",
            sub_conclusions=["Use relatable examples", "Build engagement"],
            confidence=0.8,
        ))

        # Step 4: Structure logically
        steps.append(ReasoningStep(
            step_number=4,
            description="Structure Explanation",
            analysis="Organize explanation: definition → example → practice → verification.",
            sub_conclusions=["Clear progression", "Easy to follow"],
            confidence=0.85,
        ))

        return steps

    def _reason_exercise(self, problem: str, context: Dict) -> List[ReasoningStep]:
        """Reasoning for exercise generation."""
        steps = []

        steps.append(ReasoningStep(
            step_number=1,
            description="Analyze Learning Objective",
            analysis="Determine what skill/concept should be exercised.",
            sub_conclusions=["Identify target skill", "Define success criteria"],
            confidence=0.9,
        ))

        steps.append(ReasoningStep(
            step_number=2,
            description="Design Exercise Progression",
            analysis="Create difficulty gradient: easy → medium → hard.",
            sub_conclusions=["Design variants", "Ensure pedagogy"],
            confidence=0.85,
        ))

        steps.append(ReasoningStep(
            step_number=3,
            description="Add Local Context",
            analysis="Integrate Togolese context: crops, markets, daily life.",
            sub_conclusions=["Cultural relevance", "Student engagement"],
            confidence=0.8,
        ))

        steps.append(ReasoningStep(
            step_number=4,
            description="Include Feedback Mechanism",
            analysis="Plan how to provide corrective feedback and explanation.",
            sub_conclusions=["Error identification", "Helpful guidance"],
            confidence=0.85,
        ))

        return steps

    def _reason_correction(self, problem: str, context: Dict) -> List[ReasoningStep]:
        """Reasoning for correction/verification."""
        steps = []

        steps.append(ReasoningStep(
            step_number=1,
            description="Analyze Student Response",
            analysis="Understand what the student answered and why.",
            sub_conclusions=["Identify the answer", "Understand reasoning"],
            confidence=0.9,
        ))

        steps.append(ReasoningStep(
            step_number=2,
            description="Compare to Expected Answer",
            analysis="Check against correct solution.",
            sub_conclusions=["Identify correctness", "Find errors if any"],
            confidence=0.95,
        ))

        steps.append(ReasoningStep(
            step_number=3,
            description="Diagnose Misconceptions",
            analysis="Determine if error is conceptual, computational, or careless.",
            sub_conclusions=["Error type classification", "Root cause analysis"],
            confidence=0.8,
        ))

        steps.append(ReasoningStep(
            step_number=4,
            description="Generate Corrective Feedback",
            analysis="Provide targeted explanation to address misconception.",
            sub_conclusions=["Explain correct approach", "Prevent future errors"],
            confidence=0.85,
        ))

        return steps

    def _reason_translation(self, problem: str, context: Dict) -> List[ReasoningStep]:
        """Reasoning for translation tasks."""
        steps = []

        steps.append(ReasoningStep(
            step_number=1,
            description="Understand Source Text",
            analysis="Grasp meaning, nuance, and intent of original text.",
            sub_conclusions=["Identify meaning", "Capture tone"],
            confidence=0.9,
        ))

        steps.append(ReasoningStep(
            step_number=2,
            description="Select Target Language Structures",
            analysis="Choose appropriate grammar and vocabulary in target language.",
            sub_conclusions=["Grammar selection", "Vocabulary mapping"],
            confidence=0.85,
        ))

        steps.append(ReasoningStep(
            step_number=3,
            description="Adapt for Educational Context",
            analysis="Ensure child-appropriate translation for classroom use.",
            sub_conclusions=["Simplify if needed", "Maintain accuracy"],
            confidence=0.8,
        ))

        steps.append(ReasoningStep(
            step_number=4,
            description="Verify and Cross-check",
            analysis="Back-translate mentally to ensure meaning preserved.",
            sub_conclusions=["Meaning check", "Quality assurance"],
            confidence=0.85,
        ))

        return steps

    @staticmethod
    def _aggregate_conclusions(steps: List[ReasoningStep], original_problem: str) -> str:
        """Aggregate sub-conclusions into final conclusion."""
        if not steps:
            return f"Unable to reason about: {original_problem}"

        conclusions = []
        for step in steps:
            conclusions.extend(step.sub_conclusions)

        # Create final summary
        summary_parts = [
            f"Based on {len(steps)}-step reasoning chain:",
            *conclusions[:3],  # Top 3 key conclusions
        ]

        if len(conclusions) > 3:
            summary_parts.append(f"... and {len(conclusions) - 3} more considerations.")

        return " ".join(summary_parts)
