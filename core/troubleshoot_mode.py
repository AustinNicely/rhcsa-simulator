"""
Troubleshooting mode for RHCSA Simulator.
Presents broken systems for diagnosis and repair.
"""

import logging
import random
from datetime import datetime
from tasks.registry import TaskRegistry
from core.validator import get_validator
from core.bookmarks import get_weak_area_analyzer
from core.mistakes_tracker import get_mistakes_tracker
from core.explanations import ExplanationEngine
from utils import formatters as fmt
from utils.helpers import confirm_action


logger = logging.getLogger(__name__)


class TroubleshootMode:
    """
    Troubleshooting practice mode.

    Presents broken system scenarios for users to diagnose and fix.
    """

    def __init__(self):
        """Initialize troubleshoot mode."""
        self.validator = get_validator()
        self.weak_analyzer = get_weak_area_analyzer()
        self.mistakes_tracker = get_mistakes_tracker()
        self.current_task = None
        self.clues_revealed = 0
        self.start_time = None

    def start(self):
        """Start troubleshooting mode."""
        TaskRegistry.initialize()

        fmt.clear_screen()
        fmt.print_header("TROUBLESHOOTING MODE")

        print("In this mode, you'll be presented with broken system scenarios.")
        print("Your task is to diagnose the problem and fix it.")
        print()
        print("You can request clues, but using them reduces your score.")
        print()

        # Get troubleshooting tasks
        tasks = TaskRegistry.get_tasks_by_category("troubleshooting")

        if not tasks:
            print(fmt.error("No troubleshooting tasks available"))
            return

        # Select random task or let user choose
        if confirm_action("Random scenario?", default=True):
            task_class = random.choice(tasks)
        else:
            task_class = self._select_task(tasks)
            if not task_class:
                return

        # Generate and run task
        self.current_task = task_class()
        self.current_task.generate()
        self._run_task()

    def _select_task(self, tasks):
        """Let user select a troubleshooting task."""
        print()
        print(fmt.bold("Available Troubleshooting Scenarios:"))
        print()

        for i, task_class in enumerate(tasks, 1):
            task = task_class()
            task.generate()
            print(f"  {fmt.bold(str(i) + '.')} {task.id}")
            print(f"      {fmt.dim(task.description.split(chr(10))[0][:50] + '...')}")
            print(f"      {task.points} points | {fmt.format_difficulty(task.difficulty)}")
            print()

        print(f"  {fmt.bold('Q.')} Return to main menu")
        print()

        while True:
            choice = input("Select scenario (number or Q): ").strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tasks):
                    return tasks[idx]
                else:
                    print(fmt.error("Invalid selection"))
            except ValueError:
                print(fmt.error("Please enter a number or Q"))

    def _run_task(self):
        """Run the troubleshooting task."""
        self.start_time = datetime.now()
        self.clues_revealed = 0

        fmt.clear_screen()
        self._print_task_intro()

        while True:
            print()
            print(fmt.bold("Options:"))
            print("  1. Validate my fix")
            print("  2. Request a clue")
            print("  3. Show all hints")
            print("  4. Give up")
            print()

            choice = input("Select option: ").strip()

            if choice == '1':
                if self._validate_fix():
                    break
            elif choice == '2':
                self._show_clue()
            elif choice == '3':
                self._show_all_hints()
            elif choice == '4':
                if confirm_action("Give up?", default=False):
                    self._show_solution()
                    break
            else:
                print(fmt.error("Invalid option"))

    def _print_task_intro(self):
        """Print task introduction."""
        task = self.current_task

        print()
        print("=" * 60)
        print(task.description)
        print("=" * 60)
        print()
        print(f"Points: {task.points}")
        print(f"Difficulty: {fmt.format_difficulty(task.difficulty)}")
        print()
        print(fmt.warning("Diagnose the issue and fix it on your system."))
        print(fmt.dim("Use 'Request a clue' if you need help (costs points)."))

    def _show_clue(self):
        """Show next available clue."""
        task = self.current_task

        if not hasattr(task, 'clues') or not task.clues:
            print(fmt.warning("No clues available for this task."))
            return

        self.clues_revealed += 1

        # Find appropriate clue
        for clue in task.clues:
            if clue.level == self.clues_revealed:
                print()
                print(fmt.warning(f"=== CLUE {self.clues_revealed} ==="))
                print(f"  {clue.text}")
                if clue.command:
                    print(f"  Try: {fmt.bold(clue.command)}")
                print()
                print(fmt.dim(f"(Clue penalty: -{self.clues_revealed} points)"))
                return

        # No more clues
        print(fmt.warning("No more clues available."))

    def _show_all_hints(self):
        """Show all hints for the task."""
        task = self.current_task

        if not task.hints:
            print(fmt.warning("No hints available."))
            return

        print()
        print(fmt.bold("All Hints:"))
        for i, hint in enumerate(task.hints, 1):
            print(f"  {i}. {hint}")
        print()

    def _validate_fix(self):
        """Validate the user's fix."""
        task = self.current_task

        print()
        print(fmt.bold("Validating..."))
        print()

        result = self.validator.validate_task(task)

        # Calculate score with clue penalty
        clue_penalty = self.clues_revealed * 1
        final_score = max(0, result.score - clue_penalty)

        # Display results
        print("=" * 60)
        print(fmt.bold("VALIDATION RESULTS"))
        print("=" * 60)
        print()

        for check in result.checks:
            fmt.print_check_result_detailed(
                check.name,
                check.passed,
                check.message,
                check.points,
                check.max_points
            )

        print()
        print("-" * 40)

        # Show score breakdown
        print(f"Base Score: {result.score}/{result.max_score}")
        if self.clues_revealed > 0:
            print(f"Clue Penalty: -{clue_penalty} ({self.clues_revealed} clues used)")
        print(f"Final Score: {final_score}/{result.max_score}")
        print()

        # Time taken
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            minutes = int(elapsed.total_seconds() / 60)
            seconds = int(elapsed.total_seconds() % 60)
            print(f"Time Taken: {minutes}m {seconds}s")

        print()

        if result.passed:
            print(fmt.success("PROBLEM SOLVED!"))

            # Record success
            check_results = {c.name: c.passed for c in result.checks}
            self.weak_analyzer.record_attempt(
                task.id, task.category, result.passed,
                final_score, result.max_score, check_results,
                time_seconds=elapsed.total_seconds() if self.start_time else 0
            )

            input("\nPress Enter to continue...")
            return True
        else:
            print(fmt.error("Problem not fully resolved. Keep trying!"))

            # Show what failed
            failed_checks = [c for c in result.checks if not c.passed]
            if failed_checks:
                print()
                print(fmt.bold("What's still wrong:"))
                for check in failed_checks:
                    # Get explanation
                    explanation = ExplanationEngine.get_check_explanation(check.name, False)
                    print(f"  • {check.message}")
                    if 'explanation' in explanation:
                        print(f"    {fmt.dim(explanation['explanation'])}")

            return False

    def _show_solution(self):
        """Show the full solution."""
        task = self.current_task

        print()
        print("=" * 60)
        print(fmt.warning("SOLUTION"))
        print("=" * 60)
        print()

        if task.hints:
            print(fmt.bold("Steps to fix:"))
            for i, hint in enumerate(task.hints, 1):
                print(f"  {i}. {hint}")
            print()

        if hasattr(task, 'clues') and task.clues:
            print(fmt.bold("Key insights:"))
            for clue in task.clues:
                print(f"  • {clue.text}")
                if clue.command:
                    print(f"    Command: {clue.command}")
            print()

        # Record failure
        self.mistakes_tracker.record_mistake(
            task.id, task.category, "gave_up",
            "Complete solution", "User gave up",
            task.difficulty
        )

        input("Press Enter to continue...")


def run_troubleshoot_mode():
    """Run troubleshooting mode (convenience function)."""
    mode = TroubleshootMode()
    mode.start()
