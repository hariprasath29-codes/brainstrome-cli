# 🧠 BrainStorm CLI

An adaptive, 100% offline command-line quiz game for Python developers. Built entirely with the **Python Standard Library** with **zero external dependencies and zero API keys**, featuring dynamic difficulty adjustments, heuristic distractor elimination hints, and persistent leaderboard tracking.

---

## ✨ Key Features

- 🐍 **Pure Python Focus**: 200 curated Python questions in [data/questions.json](file:///c:/Users/Public/BRAINSTROME-CLI/data/questions.json), spanning Core Python, OOP, NumPy, Pandas, Matplotlib, Seaborn, and Data Preprocessing.
- 📶 **100% Offline & Self-Contained**: Runs without internet, requiring no third-party libraries, no pip installations, and no online LLM / API keys.
- 🎯 **Configurable Round Length**: Players choose their exact round length from presets (5, 10, 15, 25 questions) or enter any custom count (1-200) directly.
- ⚡ **Adaptive Difficulty State Machine**:
  - Begins at `MEDIUM` difficulty.
  - **Correct answers** step the player up to a higher difficulty tier (`EASY` ➔ `MEDIUM` ➔ `HARD`).
  - **Incorrect answers** step down a tier to rebuild confidence (`HARD` ➔ `MEDIUM` ➔ `EASY`).
  - Base points scale with difficulty: Easy (10 pts), Medium (20 pts), Hard (30 pts).
  - Consecutive correct answers earn a **Streak Bonus Multiplier** (up to +50%).
- 💡 **Built-in Hint Helper**:
  - **50/50 Elimination**: Eliminates 2 incorrect options to help narrow down choices.
  - **Conceptual Clue**: Provides a helpful hint on Python concepts without spoiling the answer.
  - **Fair Play Scoring**: Using a hint applies a 50% point deduction for that question.
- 🏆 **Persistent JSON Leaderboard**:
  - Saved to [data/leaderboard.json](file:///c:/Users/Public/BRAINSTROME-CLI/data/leaderboard.json).
  - Displays top players sorted by score, accuracy %, and streak, with dynamic rank titles like *"🐍 Python Grandmaster"*.
- 🧹 **Leaderboard Maintenance**: Clean in-game tools to deduplicate repeat scores or remove entries.

---

## 🧭 File-by-File Architecture (How to Explain the Project)

When explaining this project in an interview or project review, walk through the files in this order:

| File | Role / Responsibility | Key Concepts to Explain |
| :--- | :--- | :--- |
| [brainstorm/models.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/models.py) | **Domain Models & Enums** | Uses `@dataclass` and `Enum` (`Difficulty`, `HintType`) for type safety and clean data contracts (`Question`, `HintResult`, `LeaderboardEntry`). |
| [brainstorm/questions.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/questions.py) | **Data Ingestion & Validation** | Parses [data/questions.json](file:///c:/Users/Public/BRAINSTROME-CLI/data/questions.json), validates schema, and indexes questions into difficulty buckets (`EASY`, `MEDIUM`, `HARD`). |
| [brainstorm/engine.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/engine.py) | **Game Rules & Adaptive Engine** | Controls question progression, dynamically transitions difficulty tiers based on answer correctness, computes streak bonuses, and enforces hint penalties. |
| [brainstorm/hints.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/hints.py) | **Hint Helper** | Offline hint generator. Delivers 50/50 elimination and conceptual clues using question metadata. |
| [brainstorm/leaderboard.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/leaderboard.py) | **JSON Persistence & Ranking** | Reads and writes [data/leaderboard.json](file:///c:/Users/Public/BRAINSTROME-CLI/data/leaderboard.json), sorts records (Score ➔ Accuracy ➔ Hints), and generates player titles. |
| [brainstorm/display.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/display.py) | **Terminal UI & ANSI Rendering** | Clean ASCII borders, ANSI color codes, and fixed-width `textwrap` word wrapping to ensure zero visual glitches on any terminal width. |
| [brainstorm/cli.py](file:///c:/Users/Public/BRAINSTROME-CLI/brainstorm/cli.py) | **Interactive CLI Controller** | Main game loop, user input handling, menu transitions (options 1 to 5), and graceful keyboard interrupt handling (`Ctrl+C`). |
| [run.py](file:///c:/Users/Public/BRAINSTROME-CLI/run.py) / [main.py](file:///c:/Users/Public/BRAINSTROME-CLI/main.py) | **Entrypoints** | Cross-platform launchers that ensure UTF-8 encoding on Windows consoles and initialize `BrainStormCLI`. |
| [tests/](file:///c:/Users/Public/BRAINSTROME-CLI/tests/) | **Automated Unit Tests** | 18 automated tests using Python's built-in `unittest` framework covering the engine, hints, leaderboard, and question validation. |

---

## 🏗️ Architecture Diagram

```
                 ┌────────────────────────────────┐
                 │       User / Terminal CLI      │
                 └───────────────┬────────────────┘
                                 │
                         [ brainstorm/cli.py ]
                                 │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
[ brainstorm/display.py ] [ brainstorm/engine.py ] [ brainstorm/leaderboard.py ]
                                 │                      │
                     ┌────────────┴────────────┐         ▼
                     │                         │     data/leaderboard.json
          [ brainstorm/questions.py ] [ brainstorm/hints.py ]
                     │                         │
                     ▼                         ▼
             data/questions.json          Built-in Hints
```

---

## 🚀 Quick Start

### 1. Launch the CLI Game
Run directly with Python 3.10+:

```bash
python main.py
```
*(Or use `python run.py`)*

### 2. Main Menu Options
```text
  [1] START QUIZ ROUND    Set question count & test skills
  [2] VIEW LEADERBOARD    Top scores & player rankings
  [3] RULES & MECHANICS   Adaptive tiers & scoring rules
  [4] QUESTION BANK       Explore topic
  [5] EXIT APPLICATION    Quit session
```

### 3. In-Game Controls
- **`A` / `B` / `C` / `D`** (or **`1` / `2` / `3` / `4`**): Select an option.
- **`H`**: Open offline hint assistant (choose distractor elimination or conceptual clue).
- **`Q`**: Quit the quiz early and record current progress.

---

## 🧪 Running Unit Tests

Run the full suite of automated unit tests:

```bash
python -m unittest discover tests -v
```

All 18 tests execute in ~0.04 seconds using pure Python standard library.
