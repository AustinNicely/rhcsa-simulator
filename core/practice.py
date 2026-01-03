"""
Practice mode for RHCSA Simulator.
"""

import logging
from tasks.registry import TaskRegistry
from core.validator import get_validator
from utils import formatters as fmt
from utils.helpers import confirm_action
from config import settings


logger = logging.getLogger(__name__)


class PracticeSession:
    """
    Practice mode session.

    Allows practicing specific categories with immediate feedback.
    """

    def __init__(self):
        """Initialize practice session."""
        self.category = None
        self.difficulty = "exam"
        self.task_count = settings.DEFAULT_PRACTICE_TASKS
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start practice session."""
        # Initialize registry
        TaskRegistry.initialize()

        # Select category
        self.category = self._select_category()
        if not self.category:
            return

        # Select difficulty
        self.difficulty = self._select_difficulty()

        # Get tasks
        tasks = TaskRegistry.get_practice_tasks(
            self.category,
            self.difficulty,
            self.task_count
        )

        if not tasks:
            print(fmt.error(f"No tasks available for {self.category}"))
            return

        # Practice each task
        for i, task in enumerate(tasks, 1):
            self._practice_task(task, i, len(tasks))

        print(fmt.success("\nPractice session complete!"))

    def _select_category(self):
        """Select practice category."""
        fmt.clear_screen()
        fmt.print_header("PRACTICE MODE - Select Category")

        categories = TaskRegistry.get_all_categories()

        if not categories:
            print(fmt.error("No task categories available"))
            return None

        # Display categories
        for i, cat in enumerate(sorted(categories), 1):
            count = TaskRegistry.get_task_count(cat)
            fmt.print_menu_option(i, fmt.format_category_name(cat), f"{count} tasks available")

        fmt.print_menu_option('Q', "Quit", "Return to main menu")

        # Get selection
        while True:
            choice = input("\nSelect category (number or Q): ").strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    return sorted(categories)[idx]
                else:
                    print(fmt.error("Invalid selection"))
            except ValueError:
                print(fmt.error("Please enter a number or Q"))

    def _select_difficulty(self):
        """Select difficulty level."""
        print()
        print(fmt.bold("Select Difficulty:"))
        fmt.print_menu_option(1, "Easy", "Simpler tasks")
        fmt.print_menu_option(2, "Exam", "Exam-level difficulty (recommended)")
        fmt.print_menu_option(3, "Hard", "Challenging tasks")

        while True:
            choice = input("\nSelect difficulty [2]: ").strip() or '2'

            if choice == '1':
                return 'easy'
            elif choice == '2':
                return 'exam'
            elif choice == '3':
                return 'hard'
            else:
                print(fmt.error("Invalid selection"))

    def _practice_task(self, task, current, total):
        """Practice a single task."""
        fmt.clear_screen()
        print(f"Practice Task {current}/{total}")
        print("=" * 60)
        print()

        # Display task
        print(fmt.bold("Task:"))
        print(task.description)
        print()
        print(fmt.bold(f"Points: {task.points}"))
        print(fmt.bold(f"Difficulty: {fmt.format_difficulty(task.difficulty)}"))
        print()

        # Show hints
        if task.hints and confirm_action("Show hints?", default=False):
            print()
            print(fmt.bold("Hints:"))
            for i, hint in enumerate(task.hints, 1):
                print(f"  {i}. {hint}")
            print()

        # Wait for completion
        input("Complete this task on your system, then press Enter to validate...")

        # Validate
        validator = get_validator()
        result = validator.validate_task(task)

        # Display result
        print()
        print(fmt.bold("Validation Results:"))
        for check in result.checks:
            fmt.print_check_result(
                check.name,
                check.passed,
                check.message,
                check.points if check.passed else 0,
                check.points
            )

        fmt.print_result_summary(result.passed, result.score, result.max_score, result.percentage)

        # Continue?
        if current < total:
            if not confirm_action("Continue to next task?", default=True):
                return


def run_practice_mode():
    """Run practice mode (convenience function)."""
    session = PracticeSession()
    session.start()
