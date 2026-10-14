"""
brainstorm.leaderboard
~~~~~~~~~~~~~~~~~~~~~~
Leaderboard storage, persistence in JSON, and ranking system.
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from brainstorm.models import LeaderboardEntry


class LeaderboardManager:
    """Manages high scores and leaderboard persistence in a JSON file."""

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "data", "leaderboard.json")

        self.filepath = filepath
        self.entries: List[LeaderboardEntry] = []
        self._load()

    def _load(self) -> None:
        """Load entries from the JSON file."""
        if not os.path.exists(self.filepath):
            self.entries = []
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_entries = data.get("leaderboard", [])
                self.entries = [
                    LeaderboardEntry.from_dict(item)
                    for item in raw_entries
                    if isinstance(item, dict)
                ]
                self._sort_entries()
        except Exception:
            # If file is corrupted or empty, start fresh without crashing
            self.entries = []

    def _sort_entries(self) -> None:
        """Sort by score descending, then accuracy descending, then fewest hints."""
        self.entries.sort(
            key=lambda e: (e.score, e.accuracy, -e.hints_used),
            reverse=True,
        )

    def save(self) -> None:
        """Persist leaderboard back to JSON file."""
        self._sort_entries()
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            payload = {
                "title": "BrainStorm CLI Leaderboard",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "leaderboard": [e.to_dict() for e in self.entries],
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError:
            pass

    def record_score(
        self,
        player_name: str,
        score: int,
        questions_answered: int,
        correct_count: int,
        highest_streak: int,
        difficulty_reached: str,
        hints_used: int,
    ) -> LeaderboardEntry:
        """Add a new game score and save it to the leaderboard."""
        clean_name = player_name.strip() or "Anonymous"
        accuracy = (correct_count / questions_answered * 100.0) if questions_answered > 0 else 0.0

        entry = LeaderboardEntry(
            player_name=clean_name[:20],
            score=score,
            questions_answered=questions_answered,
            correct_count=correct_count,
            accuracy=accuracy,
            highest_streak=highest_streak,
            difficulty_reached=difficulty_reached,
            hints_used=hints_used,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.entries.append(entry)
        self.save()
        return entry

    def get_top(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Return top N leaderboard entries."""
        return self.entries[:limit]

    def get_player_rank(self, entry: LeaderboardEntry) -> int:
        """Find the 1-based rank position of a given entry."""
        self._sort_entries()
        for idx, e in enumerate(self.entries, start=1):
            if (
                e.player_name == entry.player_name
                and e.score == entry.score
                and e.timestamp == entry.timestamp
            ):
                return idx
        return len(self.entries)

    def remove_entry(self, player_name: str, score: Optional[int] = None) -> int:
        """
        Remove entries matching player_name (case-insensitive).
        If score is provided, only removes entries matching both name and score.
        Returns the number of removed entries.
        """
        initial_len = len(self.entries)
        target = player_name.strip().lower()
        if score is not None:
            self.entries = [
                e for e in self.entries
                if not (e.player_name.strip().lower() == target and e.score == score)
            ]
        else:
            self.entries = [
                e for e in self.entries
                if e.player_name.strip().lower() != target
            ]
        removed = initial_len - len(self.entries)
        if removed > 0:
            self.save()
        return removed

    def deduplicate(self) -> int:
        """
        Keep only the single highest-scoring entry per player (case-insensitive).
        Returns the number of duplicate entries removed.
        """
        self._sort_entries()
        seen = set()
        unique = []
        for e in self.entries:
            key = e.player_name.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(e)
        removed = len(self.entries) - len(unique)
        self.entries = unique
        if removed > 0:
            self.save()
        return removed

    def clear(self) -> None:
        """Clear all entries and persist the empty leaderboard."""
        self.entries = []
        self.save()

    @staticmethod
    def get_player_title(score: int, difficulty: str) -> str:
        """Generate a fun, descriptive rank title based on score and peak difficulty."""
        diff_lower = difficulty.lower()
        if score >= 160 and diff_lower == "hard":
            return "🐍 Python Grandmaster"
        if score >= 120:
            return "⚡ Senior Pythonista"
        if score >= 80:
            return "🔧 Python Craftsman"
        if score >= 40:
            return "🌱 Python Adept"
        return "🐣 Python Apprentice"
