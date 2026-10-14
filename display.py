"""
brainstorm.display
~~~~~~~~~~~~~~~~~~
Terminal rendering, clean layout, neat ASCII borders, and ANSI formatting.
Designed to be clean, legible, and robust across all console widths and fonts.
100% self-contained terminal UI.
"""

import os
import re
import sys
import textwrap
from typing import Dict, List, Optional
from brainstorm.models import AnswerResult, Difficulty, HintResult, LeaderboardEntry, Question


# Enable Windows Virtual Terminal sequences for ANSI colors and ensure UTF-8 encoding
if os.name == "nt":
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


class Style:
    """ANSI color and styling codes with graceful fallbacks."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKE = "\033[9m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


_ANSI_REGEX = re.compile(r"\033\[[0-9;]*m")


def visible_length(text: str) -> int:
    """Return the visible character width of a string ignoring ANSI escape codes."""
    return len(_ANSI_REGEX.sub("", text))


def card_border(char: str = "-", width: int = 62, border_color: str = Style.CYAN) -> str:
    """Return a horizontal card border of exact width."""
    return f"  {border_color}+{char * width}+{Style.RESET}"


def card_row(left: str = "", right: str = "", width: int = 62, border_color: str = Style.CYAN) -> str:
    """Return a card row where left and right content are padded so borders are razor-sharp aligned."""
    vl = visible_length(left)
    vr = visible_length(right)
    pad = max(0, width - (vl + vr))
    return f"  {border_color}|{Style.RESET}{left}{' ' * pad}{right}{border_color}|{Style.RESET}"


def card_center(text: str = "", width: int = 62, border_color: str = Style.CYAN) -> str:
    """Return a centered card row with exact border alignment."""
    vl = visible_length(text)
    left_pad = max(0, (width - vl) // 2)
    right_pad = max(0, width - vl - left_pad)
    return f"  {border_color}|{Style.RESET}{' ' * left_pad}{text}{' ' * right_pad}{border_color}|{Style.RESET}"


def colorize(text: str, color_code: str) -> str:
    """Wrap text in an ANSI color code and reset."""
    return f"{color_code}{text}{Style.RESET}"


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform manner."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    """Print the main application header banner."""
    c = Style.CYAN
    r = Style.RESET
    y = Style.BRIGHT_YELLOW
    d = Style.DIM
    b = Style.BOLD

    print()
    print(card_border("=", border_color=c))
    print(card_row("", border_color=c))
    print(card_center(f"{b}{y}BRAINSTORM  ::  ADAPTIVE PYTHON CHALLENGE{r}", border_color=c))
    print(card_center(f"{d}Terminal Skill Assessment Engine  *  v2.0{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_border("=", border_color=c))


def print_player_setup_card() -> None:
    """Render the challenger player profile setup card."""
    c = Style.CYAN
    y = Style.BRIGHT_YELLOW
    b = Style.BOLD
    r = Style.RESET

    print()
    print(card_border("-", border_color=c))
    print(card_row(f"  {b}{y}PLAYER PROFILE SETUP{r}", border_color=c))
    print(card_border("-", border_color=c))
    print()


def print_main_menu(total_questions: int = 200) -> None:
    """Render the primary system menu card."""
    c = Style.CYAN
    r = Style.RESET
    w = Style.BRIGHT_WHITE
    g = Style.BRIGHT_GREEN
    d = Style.DIM
    b = Style.BOLD
    y = Style.BRIGHT_YELLOW
    m = Style.BRIGHT_MAGENTA
    red = Style.BRIGHT_RED

    print(card_border("-", border_color=c))
    print(card_row(f"  {b}{w}SYSTEM MENU{r}", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"   {b}{g}[1]{r}  {b}{'START QUIZ ROUND':<18}{r}  {d}Set question count & test skills{r}", border_color=c))
    print(card_row(f"   {b}{Style.BRIGHT_CYAN}[2]{r}  {b}{'VIEW LEADERBOARD':<18}{r}  {d}Top scores & player rankings{r}", border_color=c))
    print(card_row(f"   {b}{y}[3]{r}  {b}{'RULES & MECHANICS':<18}{r}  {d}Adaptive tiers & scoring rules{r}", border_color=c))
    print(card_row(f"   {b}{m}[4]{r}  {b}{'QUESTION BANK':<18}{r}  {d}Explore topic{r}", border_color=c))
    print(card_row(f"   {b}{red}[5]{r}  {b}{'EXIT APPLICATION':<18}{r}  {d}Quit session{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row(f"  {g}* Ready{r}  {d}|  Questions Loaded  |  100% Offline Engine{r}", border_color=c))
    print(card_border("-", border_color=c))
    print()


def print_round_setup_card(total_available: int = 200) -> None:
    """Render a clean card for selecting round question count."""
    c = Style.CYAN
    r = Style.RESET
    w = Style.BRIGHT_WHITE
    g = Style.BRIGHT_GREEN
    d = Style.DIM
    b = Style.BOLD
    y = Style.BRIGHT_YELLOW
    m = Style.BRIGHT_MAGENTA

    print(card_border("-", border_color=c))
    print(card_row(f"  {b}{y}ROUND CONFIGURATION{r}", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"  {b}Choose how many questions you want in this round:{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"   {b}{g}[1]{r}  {b}{'5 Questions':<14}{r}  {d}Quick Sprint        (approx 3 mins){r}", border_color=c))
    print(card_row(f"   {b}{Style.BRIGHT_CYAN}[2]{r}  {b}{'10 Questions':<14}{r}  {d}Standard Round      (approx 7 mins){r}", border_color=c))
    print(card_row(f"   {b}{y}[3]{r}  {b}{'15 Questions':<14}{r}  {d}Advanced Challenge  (approx 10 mins){r}", border_color=c))
    print(card_row(f"   {b}{m}[4]{r}  {b}{'25 Questions':<14}{r}  {d}Comprehensive Exam  (approx 18 mins){r}", border_color=c))
    print(card_row(f"   {b}{w}[5]{r}  {b}{'Custom Count':<14}{r}  {d}Enter any number (1 to {total_available}){r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_border("-", border_color=c))
    print()


def print_rules_card() -> None:
    """Render the game rules and scoring mechanics card."""
    c = Style.CYAN
    r = Style.RESET
    d = Style.DIM
    b = Style.BOLD
    y = Style.BRIGHT_YELLOW

    print(card_border("-", border_color=c))
    print(card_row(f"  {b}{y}RULES & SCORING MECHANICS{r}", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"  {b}1. Pure Python Focus:{r}", border_color=c))
    print(card_row(f"     {d}Evaluates data structures, dunders, closures & OOP{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"  {b}2. Adaptive Tier Scaling:{r}", border_color=c))
    print(card_row(f"     * {Style.BRIGHT_GREEN}Correct Answer{r} {d}-> Steps up tier (Easy -> Med -> Hard){r}", border_color=c))
    print(card_row(f"     * {Style.BRIGHT_RED}Wrong Answer{r}   {d}-> Steps down tier to rebuild skill{r}", border_color=c))
    print(card_row(f"     * {d}Base Points: Easy (10), Medium (20), Hard (30 pts){r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"  {b}3. Streak Multiplier:{r}", border_color=c))
    print(card_row(f"     * {d}Consecutive correct answers boost score up to +50%{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"  {b}4. Lifelines (50% Fair-Play Penalty):{r}", border_color=c))
    print(card_row(f"     * {b}[1] 50/50 Split{r}  {d}Eliminates 2 incorrect options{r}", border_color=c))
    print(card_row(f"     * {b}[2] Concept Clue{r} {d}Semantic insight on Python behavior{r}", border_color=c))
    print(card_row("", border_color=c))
    print(card_border("-", border_color=c))
    print()


def print_question_bank_card(total: int, easy: int, med: int, hard: int, topics: List[str]) -> None:
    """Render the question bank overview card."""
    c = Style.CYAN
    r = Style.RESET
    b = Style.BOLD
    y = Style.BRIGHT_YELLOW
    d = Style.DIM

    print(card_border("-", border_color=c))
    print(card_row(f"  {b}{y}QUESTION BANK OVERVIEW{r}", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row("", border_color=c))
    print(card_row(f"   * Total Challenges: {b}{total}{r}", border_color=c))
    print(card_row(f"   * {Style.BRIGHT_GREEN}[ EASY ]{r}:   {easy} questions", border_color=c))
    print(card_row(f"   * {Style.BRIGHT_YELLOW}[ MEDIUM ]{r}: {med} questions", border_color=c))
    print(card_row(f"   * {Style.BRIGHT_RED}[ HARD ]{r}:   {hard} questions", border_color=c))
    print(card_row("", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row(f"  {b}Topics Covered:{r}", border_color=c))
    for t in topics:
        print(card_row(f"    - {d}{t}{r}", border_color=c))
    print(card_border("-", border_color=c))
    print()


def format_difficulty_badge(difficulty: Difficulty) -> str:
    """Return a styled color badge for the difficulty tier."""
    if difficulty == Difficulty.EASY:
        return f"{Style.BOLD}{Style.BRIGHT_GREEN}[ EASY ]{Style.RESET}"
    if difficulty == Difficulty.MEDIUM:
        return f"{Style.BOLD}{Style.BRIGHT_YELLOW}[ MEDIUM ]{Style.RESET}"
    return f"{Style.BOLD}{Style.BRIGHT_RED}[ HARD ]{Style.RESET}"


def print_question_card(
    q_num: int,
    total_q: int,
    question: Question,
    current_score: int,
    streak: int,
    eliminated_options: List[str],
    remaining_hints: int,
) -> None:
    """Render a clean question card with options."""
    badge = format_difficulty_badge(question.difficulty)
    streak_display = f"Streak: {streak}" if streak > 0 else "Streak: 0"

    print("\n" + "=" * 66)
    print(
        f" Question {Style.BOLD}{q_num}/{total_q}{Style.RESET}  |  "
        f"Tier: {badge}  |  "
        f"Score: {Style.BRIGHT_GREEN}{current_score} pts{Style.RESET}  |  "
        f"{Style.BRIGHT_YELLOW}{streak_display}{Style.RESET}"
    )
    print(f" Topic: {Style.CYAN}{question.topic}{Style.RESET}  |  Hints Left: {Style.BRIGHT_MAGENTA}{remaining_hints}{Style.RESET}")
    print("-" * 66)

    # Format question text with word wrapping for non-code lines
    for line in question.question.split("\n"):
        if line.startswith("def ") or line.startswith("print(") or "    " in line or line.startswith("class "):
            print(f"   {Style.BRIGHT_WHITE}{line}{Style.RESET}")
        else:
            wrapped_q = textwrap.wrap(line, width=62) or [line]
            for wq in wrapped_q:
                print(f"   {Style.BOLD}{wq}{Style.RESET}")

    print("-" * 66)
    print(f" {Style.DIM}Choices:{Style.RESET}")

    # Format choices with word wrapping and hanging indent so words never break
    for key, text in sorted(question.options.items()):
        prefix = f"[{key}] "
        indent = "      "
        if key in eliminated_options:
            raw_text = f"{text} (Eliminated)"
            wrapped = textwrap.wrap(raw_text, width=56) or [raw_text]
            print(f"   {Style.DIM}{Style.STRIKE}{prefix}{wrapped[0]}{Style.RESET}")
            for extra in wrapped[1:]:
                print(f"   {Style.DIM}{Style.STRIKE}{indent}{extra}{Style.RESET}")
        else:
            wrapped = textwrap.wrap(text, width=56) or [text]
            print(f"   {Style.BRIGHT_CYAN}{prefix}{Style.RESET}{wrapped[0]}")
            for extra in wrapped[1:]:
                print(f"   {indent}{extra}")

    print("=" * 66)
    print(
        f" Enter {Style.BOLD}[A/B/C/D]{Style.RESET} to answer  |  "
        f"{Style.BOLD}[H]{Style.RESET} for Hint  |  "
        f"{Style.BOLD}[Q]{Style.RESET} to quit quiz"
    )


def print_hint_menu(remaining_hints: int, max_hints: int = 3) -> None:
    """Render a sleek, professional hint lifeline card."""
    c = Style.CYAN
    b = Style.BOLD
    m = Style.BRIGHT_MAGENTA
    d = Style.DIM
    r = Style.RESET

    print(card_border("-", border_color=c))
    print(card_center(f"{b}{m}HINT LIFELINES{r}", border_color=c))
    print(card_center(f"{d}Remaining: {remaining_hints}/{max_hints}  *  Fair Play: -50% question score{r}", border_color=c))
    print(card_border("-", border_color=c))
    print(card_row(f"   {b}[1]{r} {Style.BRIGHT_CYAN}50/50 Split{r}   {d}Eliminate 2 incorrect options{r}", border_color=c))
    print(card_row(f"   {b}[2]{r} {Style.BRIGHT_YELLOW}Concept Clue{r}  {d}Key insight on Python semantics{r}", border_color=c))
    print(card_row(f"   {b}[3]{r} {Style.WHITE}Resume Quiz{r}   {d}Return to question without penalty{r}", border_color=c))
    print(card_border("-", border_color=c))
    print()


def print_hint_box(hint: HintResult) -> None:
    """Render an in-game hint in an aligned, premium card."""
    m = Style.BRIGHT_MAGENTA
    inner_text_width = 58

    lines_to_render: List[str] = []
    for raw_line in hint.content.split("\n"):
        stripped = raw_line.strip()
        if not stripped:
            lines_to_render.append("")
        else:
            wrapped = textwrap.wrap(stripped, width=inner_text_width)
            lines_to_render.extend(wrapped)

    print()
    print(card_border("-", border_color=m))
    print(card_row(f"  {Style.BOLD}{Style.BRIGHT_YELLOW}LIFELINE ASSISTANCE{Style.RESET}", border_color=m))
    print(card_row(f"  {Style.DIM}{'-' * inner_text_width}{Style.RESET}", border_color=m))
    for line in lines_to_render:
        color = f"{Style.BOLD}{Style.BRIGHT_WHITE}" if (line.startswith("Topic:") or line.startswith("Eliminated")) else ""
        end_color = Style.RESET if color else ""
        print(card_row(f"  {color}{line}{end_color}", border_color=m))
    print(card_border("-", border_color=m))
    print()


def print_answer_feedback(result: AnswerResult) -> None:
    """Print the outcome of an answer submission clearly."""
    print()
    if result.is_correct:
        print(
            f"  {Style.BRIGHT_GREEN}{Style.BOLD}[CORRECT]{Style.RESET} "
            f"+{result.points_awarded} pts "
            f"({'[50% hint penalty applied]' if result.hint_used else '[Full points]'})"
        )
        if result.streak > 1:
            print(f"  {Style.BRIGHT_YELLOW}Streak Bonus: {result.streak} in a row!{Style.RESET}")

        if result.new_difficulty != result.old_difficulty:
            print(
                f"  {Style.BRIGHT_CYAN}ADAPTIVE LEVEL UP:{Style.RESET} "
                f"{result.old_difficulty.value.upper()} -> {Style.BOLD}{result.new_difficulty.value.upper()}{Style.RESET} "
                f"(Next question will be more challenging!)"
            )
    else:
        print(
            f"  {Style.BRIGHT_RED}{Style.BOLD}[INCORRECT]{Style.RESET} "
            f"You selected [{result.user_choice}], but the answer was {Style.BOLD}[{result.correct_choice}]{Style.RESET}."
        )
        if result.new_difficulty != result.old_difficulty:
            print(
                f"  {Style.YELLOW}ADAPTIVE EASING:{Style.RESET} "
                f"{result.old_difficulty.value.upper()} -> {Style.BOLD}{result.new_difficulty.value.upper()}{Style.RESET} "
                f"(Difficulty adjusted to help you build confidence!)"
            )

    print(f"\n  {Style.BOLD}Explanation:{Style.RESET}")
    print(f"  {result.explanation}\n")


def print_leaderboard_table(entries: List[LeaderboardEntry]) -> None:
    """Display high scores in a neat ASCII table that fits any terminal."""
    print("\n  " + "=" * 66)
    print(f"  {Style.BOLD}{Style.BRIGHT_YELLOW}                    LEADERBOARD RANKINGS{Style.RESET}")
    print("  " + "=" * 66)

    if not entries:
        print(f"    {Style.DIM}No scores recorded yet. Be the first to play!{Style.RESET}")
        print("  " + "=" * 66)
        return

    header = f"  {'Rank':<6} {'Player':<15} {'Score':<8} {'Accuracy':<10} {'Streak':<8} {'Peak Tier'}"
    print(f"{Style.BOLD}{Style.CYAN}{header}{Style.RESET}")
    print("  " + "-" * 66)

    for idx, e in enumerate(entries, start=1):
        rank_label = f"#{idx}"
        acc_str = f"{e.accuracy:.1f}%"

        if idx == 1:
            row_color = Style.BRIGHT_YELLOW
        elif idx == 2:
            row_color = Style.BRIGHT_WHITE
        elif idx == 3:
            row_color = Style.BRIGHT_CYAN
        else:
            row_color = Style.RESET

        row = (
            f"  {rank_label:<6} "
            f"{e.player_name[:14]:<15} "
            f"{e.score:<8} "
            f"{acc_str:<10} "
            f"{e.highest_streak:<8} "
            f"{e.difficulty_reached.upper()}"
        )
        print(f"{row_color}{row}{Style.RESET}")

    print("  " + "=" * 66)


def print_game_over_card(
    summary: dict,
    player_name: str,
    rank: int,
    title: str,
) -> None:
    """Display final game summary in a clean card."""
    print("\n  " + "=" * 66)
    print(f"  {Style.BOLD}{Style.BRIGHT_CYAN}                     QUIZ COMPLETED!{Style.RESET}")
    print("  " + "=" * 66)
    print(f"   Player: {Style.BOLD}{player_name}{Style.RESET}   |   Title: {Style.BRIGHT_YELLOW}{title}{Style.RESET}")
    print(f"   Standing: {Style.BOLD}Rank #{rank}{Style.RESET}")
    print("  " + "-" * 66)
    print(f"   * Final Score:          {Style.BOLD}{Style.BRIGHT_GREEN}{summary['score']} pts{Style.RESET}")
    print(f"   * Questions Answered:   {summary['total_answered']}")
    print(f"   * Correct Answers:      {summary['correct_count']} / {summary['total_answered']}")
    print(f"   * Accuracy:             {summary['accuracy']}%")
    print(f"   * Highest Streak:       {summary['highest_streak']}")
    print(f"   * Peak Tier Reached:    {summary['highest_difficulty'].upper()}")
    print(f"   * Hints Used:           {summary['hints_used']}")
    print("  " + "=" * 66 + "\n")
