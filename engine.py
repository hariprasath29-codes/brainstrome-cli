"""
brainstorm.engine
~~~~~~~~~~~~~~~~~
Adaptive quiz engine that adjusts difficulty based on player accuracy,
computes dynamic scores, and orchestrates offline hints.
"""

from typing import List, Optional, Set, Tuple
from brainstorm.hints import HintEngine
from brainstorm.models import (
    AnswerResult,
    Difficulty,
    HintResult,
    HintType,
    Question,
    QuizConfig,
)
from brainstorm.questions import QuestionBank


class QuizEngine:
    """
    State machine and rules engine for BrainStorm CLI.
    Implements adaptive difficulty:
      - Correct answer -> step up difficulty (Easy -> Medium -> Hard)
      - Incorrect answer -> step down difficulty (Hard -> Medium -> Easy)
    """

    def __init__(
        self,
        question_bank: QuestionBank,
        config: Optional[QuizConfig] = None,
        hint_engine: Optional[HintEngine] = None,
    ):
        self.bank = question_bank
        self.config = config or QuizConfig()
        self.hints = hint_engine or HintEngine()

        # Session State
        self.current_difficulty: Difficulty = self.config.starting_difficulty
        self.highest_difficulty_reached: Difficulty = self.config.starting_difficulty
        self.score: int = 0
        self.current_streak: int = 0
        self.highest_streak: int = 0
        self.correct_count: int = 0
        self.total_answered: int = 0
        self.hints_used_count: int = 0

        # Current question tracking
        self.current_question: Optional[Question] = None
        self.asked_question_ids: Set[str] = set()
        self.current_question_hint_used: bool = False
        self.current_eliminated_options: List[str] = []
        self.is_game_over: bool = False

    @property
    def remaining_hints(self) -> int:
        """Remaining hints available for this session."""
        return max(0, self.config.max_hints_per_game - self.hints_used_count)

    # Rotate preferred answer keys to prevent consecutive identical choices
    ANSWER_SEQUENCE: List[str] = ["A", "D", "B", "C"]

    def next_question(self) -> Optional[Question]:
        """
        Selects the next question based on current difficulty tier.
        Distributes answer keys across rounds for variety.
        """
        if self.total_answered >= self.config.total_questions:
            self.is_game_over = True
            return None

        target_answer = self.ANSWER_SEQUENCE[self.total_answered % len(self.ANSWER_SEQUENCE)]

        question = self.bank.sample_question(
            target_difficulty=self.current_difficulty,
            excluded_ids=self.asked_question_ids,
            preferred_answer=target_answer,
        )

        if question is None:
            # No more unasked questions available
            self.is_game_over = True
            return None

        self.current_question = question
        self.asked_question_ids.add(question.id)
        self.current_question_hint_used = False
        self.current_eliminated_options = []
        return question

    def request_hint(self, hint_type: HintType) -> Tuple[Optional[HintResult], Optional[str]]:
        """
        Request a hint for the current active question.
        Returns (HintResult, error_message).
        """
        if self.current_question is None:
            return None, "No active question."

        if self.remaining_hints <= 0:
            return None, "You have reached the maximum allowed hints for this game."

        if self.current_question_hint_used and hint_type == HintType.ELIMINATION and self.current_eliminated_options:
            return None, "Elimination hint has already been applied to this question."

        # Generate hint from hint engine
        hint_result = self.hints.get_hint(self.current_question, hint_type)

        self.hints_used_count += 1
        self.current_question_hint_used = True

        if hint_result.hint_type == HintType.ELIMINATION:
            self.current_eliminated_options.extend(hint_result.eliminated_options)

        return hint_result, None

    def submit_answer(self, user_choice: str) -> AnswerResult:
        """
        Evaluate the player's selected option and adapt difficulty for the next question.
        """
        if self.current_question is None:
            raise ValueError("No active question to answer.")

        clean_choice = user_choice.strip().upper()
        is_correct = (clean_choice == self.current_question.correct_answer.upper())

        old_difficulty = self.current_difficulty
        points_awarded = 0

        self.total_answered += 1

        if is_correct:
            self.correct_count += 1
            self.current_streak += 1
            if self.current_streak > self.highest_streak:
                self.highest_streak = self.current_streak

            # Calculate score with streak bonus and hint penalty
            base_points = self.current_question.difficulty.base_points
            # Streak bonus: +10% per streak point (up to +50%)
            streak_multiplier = 1.0 + min(0.5, (self.current_streak - 1) * 0.1)
            calculated_points = int(round(base_points * streak_multiplier))

            if self.current_question_hint_used:
                calculated_points = int(round(calculated_points * self.config.hint_penalty_multiplier))
                # Ensure minimum 1 point on correct answer
                calculated_points = max(1, calculated_points)

            points_awarded = calculated_points
            self.score += points_awarded

            # Adaptive upgrade: Correct answer moves to harder difficulty
            new_difficulty = self.current_difficulty.next_harder()
        else:
            self.current_streak = 0
            points_awarded = 0

            # Adaptive downgrade: Wrong answer moves to easier difficulty
            new_difficulty = self.current_difficulty.next_easier()

        self.current_difficulty = new_difficulty

        # Track peak difficulty achieved
        diff_rank = {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}
        if diff_rank[new_difficulty] > diff_rank[self.highest_difficulty_reached]:
            self.highest_difficulty_reached = new_difficulty

        result = AnswerResult(
            is_correct=is_correct,
            user_choice=clean_choice,
            correct_choice=self.current_question.correct_answer,
            points_awarded=points_awarded,
            streak=self.current_streak,
            old_difficulty=old_difficulty,
            new_difficulty=new_difficulty,
            explanation=self.current_question.explanation,
            hint_used=self.current_question_hint_used,
        )

        return result

    @property
    def accuracy_percentage(self) -> float:
        """Player's accuracy percentage so far."""
        if self.total_answered == 0:
            return 0.0
        return (self.correct_count / self.total_answered) * 100.0

    def get_summary(self) -> dict:
        """Returns end-of-game performance metrics."""
        return {
            "score": self.score,
            "total_answered": self.total_answered,
            "correct_count": self.correct_count,
            "accuracy": round(self.accuracy_percentage, 1),
            "highest_streak": self.highest_streak,
            "highest_difficulty": self.highest_difficulty_reached.value,
            "hints_used": self.hints_used_count,
        }
