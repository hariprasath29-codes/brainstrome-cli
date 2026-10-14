"""
brainstorm.hints
~~~~~~~~~~~~~~~~
Hint helper for the BrainStorm quiz game.
Provides 50/50 distractor elimination and conceptual clues
from local question data.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from brainstorm.models import HintResult, HintType, Question


class BaseHintProvider(ABC):
    """Base class for hint providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def is_online(self) -> bool:
        return False

    @abstractmethod
    def generate_hint(self, question: Question, hint_type: HintType) -> HintResult:
        pass


class OfflineHintProvider(BaseHintProvider):
    """
    Local hint generator.
    Filters out incorrect choices for 50/50 hints and pulls
    concept tips from question metadata.
    """

    @property
    def name(self) -> str:
        return "BrainStorm Hint Helper"

    def generate_hint(self, question: Question, hint_type: HintType) -> HintResult:
        if hint_type == HintType.ELIMINATION:
            return self._generate_elimination(question)
        return self._generate_conceptual(question)

    def _generate_elimination(self, question: Question) -> HintResult:
        """Eliminate up to 2 incorrect choices."""
        wrong_keys = [
            k for k in question.options.keys()
            if k.upper() != question.correct_answer.upper()
        ]

        # Use predefined wrong options if available, otherwise pick the first wrong ones
        candidates = [c for c in question.elimination_candidates if c in wrong_keys]
        if len(candidates) < 2 and len(wrong_keys) >= 2:
            remaining = [k for k in wrong_keys if k not in candidates]
            candidates.extend(remaining[: 2 - len(candidates)])
        elif not candidates:
            candidates = wrong_keys[:2]

        eliminated = candidates[:2]

        lines = [
            f"Topic: {question.topic}",
            "",
            "Eliminated wrong options:",
        ]
        for opt_key in eliminated:
            opt_val = question.options.get(opt_key, "")
            lines.append(f"  • [{opt_key}] {opt_val}")

        remaining_count = len(question.options) - len(eliminated)
        lines.append("")
        lines.append(f"Focus on the remaining {remaining_count} choices.")

        return HintResult(
            hint_type=HintType.ELIMINATION,
            content="\n".join(lines),
            eliminated_options=eliminated,
            provider_name=self.name,
        )

    def _generate_conceptual(self, question: Question) -> HintResult:
        """Provide a conceptual clue without giving away the exact answer."""
        if question.conceptual_hint:
            clue = question.conceptual_hint
        else:
            clue = f"Review the core Python concepts around '{question.topic}'."

        lines = [
            f"Topic: {question.topic}",
            "",
            f"\"{clue}\"",
            "",
            "Tip: Think about how Python evaluates this line by line.",
        ]

        return HintResult(
            hint_type=HintType.CONCEPTUAL,
            content="\n".join(lines),
            eliminated_options=[],
            provider_name=self.name,
        )


class HintEngine:
    """Manages hint requests for the active quiz."""

    def __init__(self):
        self._provider: BaseHintProvider = OfflineHintProvider()

    @property
    def active_provider_name(self) -> str:
        return self._provider.name

    @property
    def is_online(self) -> bool:
        return False

    def get_hint(self, question: Question, hint_type: HintType) -> HintResult:
        """Fetch a hint for the current question."""
        return self._provider.generate_hint(question, hint_type)

    def generate_hint(
        self, question: Question, hint_type: HintType
    ) -> Tuple[Optional[HintResult], Optional[str]]:
        """Fetch a hint, returning (result, error) tuple."""
        try:
            res = self._provider.generate_hint(question, hint_type)
            return res, None
        except Exception as e:
            return None, str(e)
