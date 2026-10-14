"""
brainstorm.cli
~~~~~~~~~~~~~~
Interactive Command-Line Interface and game loop for BrainStorm CLI.
"""

import sys
import time
from typing import Optional

from brainstorm.hints import HintEngine
from brainstorm.display import (
    Style,
    clear_screen,
    format_difficulty_badge,
    print_answer_feedback,
    print_banner,
    print_game_over_card,
    print_hint_box,
    print_hint_menu,
    print_leaderboard_table,
    print_main_menu,
    print_player_setup_card,
    print_question_bank_card,
    print_question_card,
    print_round_setup_card,
    print_rules_card,
)
from brainstorm.engine import QuizEngine
from brainstorm.leaderboard import LeaderboardManager
from brainstorm.models import Difficulty, HintType, QuizConfig
from brainstorm.questions import QuestionBank, QuestionLoadError


class BrainStormCLI:
    """Main CLI Application controller."""

    def __init__(self):
        try:
            self.question_bank = QuestionBank()
        except QuestionLoadError as err:
            print(f"{Style.BRIGHT_RED}Error loading questions: {err}{Style.RESET}")
            sys.exit(1)

        self.leaderboard_manager = LeaderboardManager()
        self.hint_engine = HintEngine()
        self.config = QuizConfig(total_questions=10)

    def run(self) -> None:
        """Main application lifecycle loop."""
        try:
            while True:
                self._show_main_menu()
                choice = input(f"  {Style.BOLD}Select an option [1-5]: {Style.RESET}").strip()
                if choice == "1":
                    self._play_quiz()
                elif choice == "2":
                    self._view_leaderboard()
                elif choice == "3":
                    self._show_how_to_play()
                elif choice == "4":
                    self._browse_questions()
                elif choice == "5" or choice.lower() in ("q", "exit", "quit"):
                    print(f"\n{Style.BRIGHT_CYAN}Thank you for playing BrainStorm CLI! Happy Python coding! 🐍{Style.RESET}\n")
                    break
                else:
                    print(f"\n  {Style.YELLOW}Invalid selection. Please choose between 1 and 5.{Style.RESET}")
                    time.sleep(1)
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Style.BRIGHT_YELLOW}Session closed. Goodbye! 🐍{Style.RESET}\n")
            sys.exit(0)

    def _show_main_menu(self) -> None:
        """Display the primary menu card."""
        clear_screen()
        print_banner()
        print_main_menu(self.question_bank.get_question_count())

    def _play_quiz(self) -> None:
        """Run an adaptive quiz session with custom round length."""
        clear_screen()
        print_banner()
        print_player_setup_card()
        player_name = input(f"  {Style.BOLD}Enter Challenger Name (or press Enter for 'Player 1'): {Style.RESET}").strip()
        if not player_name:
            player_name = "Player 1"

        total_available = self.question_bank.get_question_count()
        print_round_setup_card(total_available)

        num_questions = 0
        preset_map = {
            "1": min(5, total_available),
            "2": min(10, total_available),
            "3": min(15, total_available),
            "4": min(25, total_available),
        }

        while True:
            round_input = input(f"  {Style.BOLD}Select [1-5] or type question count directly (1-{total_available}): {Style.RESET}").strip()
            if round_input in preset_map:
                num_questions = preset_map[round_input]
                break
            elif round_input == "5":
                while True:
                    custom_str = input(f"  {Style.BOLD}Enter exact number of questions to play (1-{total_available}): {Style.RESET}").strip()
                    try:
                        c_val = int(custom_str)
                        if 1 <= c_val <= total_available:
                            num_questions = c_val
                            break
                        else:
                            print(f"  {Style.YELLOW}Please enter a number between 1 and {total_available}.{Style.RESET}")
                    except ValueError:
                        print(f"  {Style.YELLOW}Please enter a valid number.{Style.RESET}")
                break
            else:
                try:
                    val = int(round_input)
                    if 1 <= val <= total_available:
                        num_questions = val
                        break
                    else:
                        print(f"  {Style.YELLOW}Please choose an option [1-5] or enter a number between 1 and {total_available}.{Style.RESET}")
                except ValueError:
                    print(f"  {Style.YELLOW}Invalid entry. Choose an option [1-5] or enter a number between 1 and {total_available}.{Style.RESET}")

        print(f"\n  {Style.BRIGHT_GREEN}Configured round with {num_questions} questions for {player_name}. Starting challenge...{Style.RESET}")
        time.sleep(1)

        session_config = QuizConfig(
            total_questions=num_questions,
            starting_difficulty=self.config.starting_difficulty,
            streak_threshold_for_upgrade=self.config.streak_threshold_for_upgrade,
            streak_threshold_for_downgrade=self.config.streak_threshold_for_downgrade,
            hint_penalty_multiplier=self.config.hint_penalty_multiplier,
            max_hints_per_game=self.config.max_hints_per_game,
        )

        engine = QuizEngine(
            question_bank=self.question_bank,
            config=session_config,
            hint_engine=self.hint_engine,
        )

        q_counter = 0

        while True:
            question = engine.next_question()
            if question is None:
                break

            q_counter += 1
            answered = False

            while not answered:
                clear_screen()
                print_banner()
                print_question_card(
                    q_num=q_counter,
                    total_q=engine.config.total_questions,
                    question=question,
                    current_score=engine.score,
                    streak=engine.current_streak,
                    eliminated_options=engine.current_eliminated_options,
                    remaining_hints=engine.remaining_hints,
                )

                user_input = input(f"\n{Style.BOLD}Your choice: {Style.RESET}").strip().upper()

                # Map numeric inputs (1 -> A, 2 -> B, 3 -> C, 4 -> D)
                numeric_map = {"1": "A", "2": "B", "3": "C", "4": "D"}
                if user_input in numeric_map:
                    user_input = numeric_map[user_input]

                if user_input in ("Q", "QUIT"):
                    confirm = input(f"{Style.YELLOW}Are you sure you want to end this game early? [y/N]: {Style.RESET}").strip().lower()
                    if confirm == "y":
                        engine.is_game_over = True
                        break
                    continue

                if user_input in ("H", "HINT"):
                    self._handle_hint_request(engine)
                    continue

                if user_input in question.options:
                    if user_input in engine.current_eliminated_options:
                        print(f"\n{Style.YELLOW}Notice: Option [{user_input}] was eliminated as incorrect!{Style.RESET}")
                        reconfirm = input("Do you still want to choose it? [y/N]: ").strip().lower()
                        if reconfirm != "y":
                            continue

                    # Submit answer
                    result = engine.submit_answer(user_input)
                    clear_screen()
                    print_banner()
                    print_answer_feedback(result)
                    input(f"{Style.DIM}Press [ENTER] to continue to the next question...{Style.RESET}")
                    answered = True
                else:
                    print(f"{Style.BRIGHT_RED}Invalid choice! Enter A, B, C, D, H for Hint, or Q to quit.{Style.RESET}")
                    time.sleep(1.2)

            if engine.is_game_over:
                break

        # Quiz finished: Calculate final score and record to leaderboard
        if engine.total_answered > 0:
            summary = engine.get_summary()
            entry = self.leaderboard_manager.record_score(
                player_name=player_name,
                score=summary["score"],
                questions_answered=summary["total_answered"],
                correct_count=summary["correct_count"],
                highest_streak=summary["highest_streak"],
                difficulty_reached=summary["highest_difficulty"],
                hints_used=summary["hints_used"],
            )
            rank = self.leaderboard_manager.get_player_rank(entry)
            title = self.leaderboard_manager.get_player_title(summary["score"], summary["highest_difficulty"])

            clear_screen()
            print_banner()
            print_game_over_card(
                summary=summary,
                player_name=player_name,
                rank=rank,
                title=title,
            )
        else:
            print(f"\n{Style.YELLOW}Game ended before answering any questions.{Style.RESET}")

        input(f"{Style.DIM}Press [ENTER] to return to Main Menu...{Style.RESET}")

    def _handle_hint_request(self, engine: QuizEngine) -> None:
        """Interactive hint sub-menu."""
        if engine.remaining_hints <= 0:
            print(f"\n  {Style.BRIGHT_RED}No hint lifelines remaining for this session (Max {self.config.max_hints_per_game}).{Style.RESET}")
            time.sleep(1.2)
            return

        print_hint_menu(engine.remaining_hints, self.config.max_hints_per_game)
        hint_choice = input(f"  {Style.BOLD}Select lifeline [1-3]: {Style.RESET}").strip()

        if hint_choice == "1":
            hint_res, err = engine.request_hint(HintType.ELIMINATION)
            if err:
                print(f"  {Style.YELLOW}{err}{Style.RESET}")
                time.sleep(1.2)
            elif hint_res:
                print_hint_box(hint_res)
                input(f"  {Style.DIM}Press [ENTER] to return to the question...{Style.RESET}")

        elif hint_choice == "2":
            hint_res, err = engine.request_hint(HintType.CONCEPTUAL)
            if err:
                print(f"  {Style.YELLOW}{err}{Style.RESET}")
                time.sleep(1.2)
            elif hint_res:
                print_hint_box(hint_res)
                input(f"  {Style.DIM}Press [ENTER] to return to the question...{Style.RESET}")

        elif hint_choice == "3":
            return
        else:
            print(f"  {Style.YELLOW}Invalid selection.{Style.RESET}")
            time.sleep(0.8)

    def _view_leaderboard(self) -> None:
        """Display top scores with options to deduplicate or remove entries."""
        while True:
            clear_screen()
            print_banner()
            entries = self.leaderboard_manager.get_top(limit=15)
            print_leaderboard_table(entries)
            print(f"\n  {Style.DIM}[ENTER] Back to menu  |  [D] Deduplicate  |  [R] Remove player entry{Style.RESET}")
            cmd = input(f"  {Style.BOLD}Selection: {Style.RESET}").strip().lower()
            if cmd == "d":
                removed = self.leaderboard_manager.deduplicate()
                if removed:
                    print(f"\n  {Style.BRIGHT_GREEN}Cleaned up {removed} duplicate entries (kept best scores)!{Style.RESET}")
                else:
                    print(f"\n  {Style.YELLOW}No duplicate entries found.{Style.RESET}")
                time.sleep(1.2)
            elif cmd == "r":
                name = input(f"  {Style.BOLD}Enter player name to remove: {Style.RESET}").strip()
                if name:
                    count = self.leaderboard_manager.remove_entry(name)
                    if count:
                        print(f"\n  {Style.BRIGHT_GREEN}Removed {count} entry(ies) for '{name}'.{Style.RESET}")
                    else:
                        print(f"\n  {Style.YELLOW}No entries found for player '{name}'.{Style.RESET}")
                    time.sleep(1.2)
            else:
                break

    def _show_how_to_play(self) -> None:
        """Print game rules, adaptive difficulty details, and scoring mechanics."""
        clear_screen()
        print_banner()
        print_rules_card()
        input(f"  {Style.DIM}Press [ENTER] to return to Main Menu...{Style.RESET}")

    def _browse_questions(self) -> None:
        """Explore available questions by difficulty."""
        clear_screen()
        print_banner()
        total = self.question_bank.get_question_count()
        easy_cnt = self.question_bank.get_question_count(Difficulty.EASY)
        med_cnt = self.question_bank.get_question_count(Difficulty.MEDIUM)
        hard_cnt = self.question_bank.get_question_count(Difficulty.HARD)
        topics = sorted({q.topic for q in self.question_bank.all_questions})

        print_question_bank_card(total, easy_cnt, med_cnt, hard_cnt, topics)
        input(f"  {Style.DIM}Press [ENTER] to return to Main Menu...{Style.RESET}")
