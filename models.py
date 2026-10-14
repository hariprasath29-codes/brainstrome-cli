"""
brainstorm.models
~~~~~~~~~~~~~~~~~
Data models and type definitions for the BrainStorm CLI quiz game.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Difficulty(str, Enum):
    """Adaptive difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @classmethod
    def from_str(cls, value: str) -> "Difficulty":
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.MEDIUM

    def next_harder(self) -> "Difficulty":
        """Return the next higher difficulty tier."""
        if self == Difficulty.EASY:
            return Difficulty.MEDIUM
        return Difficulty.HARD

    def next_easier(self) -> "Difficulty":
        """Return the next lower difficulty tier."""
        if self == Difficulty.HARD:
            return Difficulty.MEDIUM
        return Difficulty.EASY

    @property
    def badge_color(self) -> str:
        """Color indicator for terminal display."""
        if self == Difficulty.EASY:
            return "green"
        if self == Difficulty.MEDIUM:
            return "yellow"
        return "red"

    @property
    def base_points(self) -> int:
        """Base score awarded for correctly answering this difficulty."""
        mapping = {
            Difficulty.EASY: 10,
            Difficulty.MEDIUM: 20,
            Difficulty.HARD: 30,
        }
        return mapping[self]


@dataclass
class Question:
    """Represents a single Python multiple-choice question."""
    id: str
    difficulty: Difficulty
    topic: str
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    conceptual_hint: str
    elimination_candidates: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        diff = Difficulty.from_str(data.get("difficulty", "medium"))
        raw_options = data.get("options", {})
        correct_ans = str(data.get("correct_answer", "")).strip().upper()

        # Fallback elimination candidates if not provided
        elim_candidates = data.get("elimination_candidates", [])
        if not elim_candidates:
            # Pick wrong options automatically
            elim_candidates = [
                key for key in raw_options.keys()
                if key.upper() != correct_ans
            ][:2]

        return cls(
            id=str(data.get("id", "q_unknown")),
            difficulty=diff,
            topic=str(data.get("topic", "Python General")),
            question=str(data.get("question", "")).strip(),
            options={str(k).upper(): str(v).strip() for k, v in raw_options.items()},
            correct_answer=correct_ans,
            explanation=str(data.get("explanation", "")).strip(),
            conceptual_hint=str(data.get("conceptual_hint", "")).strip(),
            elimination_candidates=[str(c).upper() for c in elim_candidates],
        )


class HintType(str, Enum):
    """Types of offline assistance."""
    ELIMINATION = "elimination"
    CONCEPTUAL = "conceptual"


@dataclass
class HintResult:
    """Holds the generated offline hint."""
    hint_type: HintType
    content: str
    eliminated_options: List[str] = field(default_factory=list)
    provider_name: str = "BrainStorm Hint Helper"


@dataclass
class AnswerResult:
    """Outcome of an answer evaluation."""
    is_correct: bool
    user_choice: str
    correct_choice: str
    points_awarded: int
    streak: int
    old_difficulty: Difficulty
    new_difficulty: Difficulty
    explanation: str
    hint_used: bool


@dataclass
class LeaderboardEntry:
    """Record saved to the persistent leaderboard."""
    player_name: str
    score: int
    questions_answered: int
    correct_count: int
    accuracy: float
    highest_streak: int
    difficulty_reached: str
    hints_used: int
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name,
            "score": self.score,
            "questions_answered": self.questions_answered,
            "correct_count": self.correct_count,
            "accuracy": round(self.accuracy, 1),
            "highest_streak": self.highest_streak,
            "difficulty_reached": self.difficulty_reached,
            "hints_used": self.hints_used,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LeaderboardEntry":
        return cls(
            player_name=str(data.get("player_name", "Anonymous")),
            score=int(data.get("score", 0)),
            questions_answered=int(data.get("questions_answered", 0)),
            correct_count=int(data.get("correct_count", 0)),
            accuracy=float(data.get("accuracy", 0.0)),
            highest_streak=int(data.get("highest_streak", 0)),
            difficulty_reached=str(data.get("difficulty_reached", "easy")),
            hints_used=int(data.get("hints_used", 0)),
            timestamp=str(data.get("timestamp", "")),
        )


@dataclass
class QuizConfig:
    """Game session parameters."""
    total_questions: int = 10
    starting_difficulty: Difficulty = Difficulty.MEDIUM
    streak_threshold_for_upgrade: int = 1   # 1 correct pushes difficulty up
    streak_threshold_for_downgrade: int = 1 # 1 wrong pushes difficulty down
    hint_penalty_multiplier: float = 0.5    # Halves question points if hint used
    max_hints_per_game: int = 3
