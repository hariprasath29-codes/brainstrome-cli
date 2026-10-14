"""
brainstorm.questions
~~~~~~~~~~~~~~~~~~~~
Question loading, validation, and pool organization.
"""

import json
import os
import random
from typing import Dict, List, Optional, Set
from brainstorm.models import Difficulty, Question


class QuestionLoadError(Exception):
    """Raised when question bank fails to load or validate."""
    pass


class QuestionBank:
    """Manages the pool of Python multiple-choice questions."""

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            # Default to data/questions.json relative to the repository
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "data", "questions.json")

        self.filepath = filepath
        self.questions_by_difficulty: Dict[Difficulty, List[Question]] = {
            Difficulty.EASY: [],
            Difficulty.MEDIUM: [],
            Difficulty.HARD: [],
        }
        self.all_questions: List[Question] = []
        self._load()

    def _load(self) -> None:
        """Load and validate questions from the JSON file."""
        if not os.path.exists(self.filepath):
            raise QuestionLoadError(f"Questions file not found at: {self.filepath}")

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise QuestionLoadError(f"Malformed JSON in questions file: {exc}")
        except Exception as exc:
            raise QuestionLoadError(f"Failed to read questions file: {exc}")

        raw_questions = data.get("questions", [])
        if not raw_questions or not isinstance(raw_questions, list):
            raise QuestionLoadError("Questions file must contain a non-empty 'questions' array.")

        seen_ids: Set[str] = set()

        for idx, item in enumerate(raw_questions, start=1):
            if not isinstance(item, dict):
                continue

            q_id = item.get("id", f"q_{idx}")
            if q_id in seen_ids:
                continue
            seen_ids.add(q_id)

            # Validate question contents
            question_text = item.get("question", "").strip()
            options = item.get("options", {})
            correct_ans = str(item.get("correct_answer", "")).strip().upper()

            if not question_text:
                continue
            if not isinstance(options, dict) or len(options) < 2:
                continue
            if correct_ans not in options:
                # Invalid correct answer key
                continue

            q = Question.from_dict(item)
            self.all_questions.append(q)
            self.questions_by_difficulty[q.difficulty].append(q)

        total_loaded = len(self.all_questions)
        if total_loaded == 0:
            raise QuestionLoadError("No valid Python questions could be loaded from the JSON file.")

    def get_question_count(self, difficulty: Optional[Difficulty] = None) -> int:
        """Return the number of available questions in total or per tier."""
        if difficulty is not None:
            return len(self.questions_by_difficulty.get(difficulty, []))
        return len(self.all_questions)

    def sample_question(
        self,
        target_difficulty: Difficulty,
        excluded_ids: Set[str],
        preferred_answer: Optional[str] = None,
    ) -> Optional[Question]:
        """
        Sample an unasked question from target difficulty.
        Prioritizes questions matching preferred_answer if provided.
        Uses random.choice so that questions change across different game sessions.
        """
        candidates = [
            q for q in self.questions_by_difficulty[target_difficulty]
            if q.id not in excluded_ids
        ]
        if candidates:
            if preferred_answer:
                matching = [q for q in candidates if q.correct_answer.upper() == preferred_answer.upper()]
                if matching:
                    return random.choice(matching)
            return random.choice(candidates)

        # Fallback sequence: medium -> easy/hard
        fallback_order: List[Difficulty] = []
        if target_difficulty == Difficulty.HARD:
            fallback_order = [Difficulty.MEDIUM, Difficulty.EASY]
        elif target_difficulty == Difficulty.EASY:
            fallback_order = [Difficulty.MEDIUM, Difficulty.HARD]
        else:  # MEDIUM
            fallback_order = [Difficulty.EASY, Difficulty.HARD]

        for alt_diff in fallback_order:
            alt_candidates = [
                q for q in self.questions_by_difficulty[alt_diff]
                if q.id not in excluded_ids
            ]
            if alt_candidates:
                if preferred_answer:
                    alt_matching = [q for q in alt_candidates if q.correct_answer.upper() == preferred_answer.upper()]
                    if alt_matching:
                        return random.choice(alt_matching)
                return random.choice(alt_candidates)

        return None

