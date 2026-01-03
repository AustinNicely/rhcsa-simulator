"""
Exam mode orchestrator for RHCSA Simulator.
"""

import time
import logging
from datetime import datetime, timedelta
from config import settings
from tasks.registry import TaskRegistry
from core.validator import get_validator
from core.results import ExamResult, TaskResult, get_results_manager
from utils import formatters as fmt
from utils.helpers import generate_id, format_timedelta, confirm_action


logger = logging.getLogger(__name__)


class ExamSession:
    """
    Exam mode session orchestrator.

    Manages task generation, display, timer, and validation.
    """

    def __init__(self, task_count=None, timer_enabled=True, duration_minutes=None):
        """
        Initialize exam session.

        Args:
            task_count (int): Number of tasks (default: from settings)
            timer_enabled (bool): Whether to enable timer
            duration_minutes (int): Exam duration (default: from settings)
        """
        self.task_count = task_count or settings.DEFAULT_EXAM_TASKS
        self.timer_enabled = timer_enabled
        self.duration_minutes = duration_minutes or settings.DEFAULT_EXAM_DURATION
        self.start_time = None
        self.end_time = None
        self.tasks = []
        self.exam_id = generate_id("exam")
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start the exam session."""
        # Initialize task registry
        TaskRegistry.initialize()

        # Display welcome screen
        self._display_welcome()

        # Confirm to start
        if not confirm_action("Ready to start the exam?", default=True):
            print("Exam cancelled.")
            return None

        # Generate tasks
        print("\nGenerating exam tasks...")
        self.tasks = TaskRegistry.get_exam_tasks(self.task_count)

        if not self.tasks:
            print(fmt.error("Error: Could not generate exam tasks"))
            self.logger.error("Failed to generate exam tasks")
            return None

        print(fmt.success(f"Generated {len(self.tasks)} tasks"))

        # Display tasks
        self._display_tasks()

        # Start timer
        self.start_time = datetime.now()

        if self.timer_enabled:
            print(f"\n{fmt.warning('Timer started!')} You have {self.duration_minutes} minutes.")
            print(f"Exam ends at: {(self.start_time + timedelta(minutes=self.duration_minutes)).strftime('%H:%M:%S')}")
        else:
            print(f"\n{fmt.info('Exam started!')} (No time limit)")

        print("\nComplete the tasks on your system, then return here to validate your work.")
        print("=" * 60)

    def _display_welcome(self):
        """Display exam welcome screen."""
        fmt.clear_screen()
        fmt.print_header("RHCSA MOCK EXAM", char='=')

        print(fmt.bold("Exam Information:"))
        print(f"  Tasks: {self.task_count}")
        print(f"  Duration: {self.duration_minutes} minutes" if self.timer_enabled else "  Duration: No time limit")
        print(f"  Pass threshold: {settings.EXAM_PASS_THRESHOLD * 100:.0f}%")
        print()

        print(fmt.bold("Instructions:"))
        print("  1. Read all tasks carefully before starting")
        print("  2. Complete tasks on your Linux system")
        print("  3. Return here when ready to validate")
        print("  4. You can validate multiple times")
        print()

        print(fmt.warning("Note: This simulator only validates your work. It does NOT make changes to your system."))
        print()

    def _display_tasks(self):
        """Display all exam tasks."""
        fmt.print_header("EXAM TASKS")

        total_points = sum(task.points for task in self.tasks)

        for i, task in enumerate(self, 1):
            fmt.print_task(i, task.description, task.points)

        print()
        print(fmt.bold(f"Total Points: {total_points}"))
        print("=" * 60)

    def validate_all(self):
        """
        Validate all tasks and generate exam result.

        Returns:
            ExamResult: Exam result
        """
        self.end_time = datetime.now()

        print()
        fmt.print_header("VALIDATING YOUR WORK")

        # Get validator
        validator = get_validator()

        # Validate each task
        validation_results = []
        task_results = []

        for i, task in enumerate(self.tasks, 1):
            print(f"\nValidating Task {i}/{len(self.tasks)}: {task.id}")

            result = validator.validate_task(task)
            validation_results.append(result)

            # Create task result
            task_result = TaskResult(
                task_id=task.id,
                category=task.category,
                difficulty=task.difficulty,
                description=task.description,
                score=result.score,
                max_score=result.max_score,
                passed=result.passed
            )
            task_results.append(task_result)

            # Display result
            self._display_task_result(i, task, result)

        # Calculate totals
        total_score, max_score, percentage = validator.calculate_total_score(validation_results)
        passed = percentage >= (settings.EXAM_PASS_THRESHOLD * 100)

        # Create exam result
        duration = (self.end_time - self.start_time).total_seconds()
        exam_result = ExamResult(
            exam_id=self.exam_id,
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            duration_seconds=int(duration),
            timer_enabled=self.timer_enabled,
            task_results=task_results,
            total_score=total_score,
            max_score=max_score,
            passed=passed
        )

        # Display final report
        self._display_final_report(exam_result)

        # Save result
        results_mgr = get_results_manager()
        filepath = results_mgr.save_result(exam_result)
        if filepath:
            print(f"\n{fmt.success('Result saved to:')} {filepath}")

        return exam_result

    def _display_task_result(self, task_num, task, result):
        """Display result for a single task."""
        print(f"\n{fmt.bold(f'Task {task_num}:')} {task.description[:60]}...")

        # Display checks
        for check in result.checks:
            fmt.print_check_result(
                check.name,
                check.passed,
                check.message,
                check.points if check.passed else 0,
                check.points
            )

        # Display summary
        status = fmt.success("PASS") if result.passed else fmt.error("FAIL")
        print(f"  Score: {result.score}/{result.max_score} points ({result.percentage:.0f}%) - {status}")

    def _display_final_report(self, exam_result):
        """Display final exam report."""
        fmt.print_header("EXAM RESULTS")

        # Overall result
        print(fmt.bold("Overall Performance:"))
        print(f"  Total Score: {exam_result.total_score}/{exam_result.max_score} points")
        print(f"  Percentage: {exam_result.percentage:.1f}%")
        print(f"  Tasks Passed: {sum(1 for t in exam_result.task_results if t.passed)}/{len(exam_result.task_results)}")
        print(f"  Duration: {format_timedelta(timedelta(seconds=exam_result.duration_seconds))}")
        print()

        # Pass/Fail
        if exam_result.passed:
            print(fmt.success(f"  ✓ PASSED (Required: {exam_result.pass_threshold * 100:.0f}%)"))
        else:
            print(fmt.error(f"  ✗ FAILED (Required: {exam_result.pass_threshold * 100:.0f}%)"))
        print()

        # Category breakdown
        print(fmt.bold("Performance by Category:"))
        breakdown = exam_result.get_category_breakdown()

        for category, stats in sorted(breakdown.items()):
            from utils.formatters import format_category_name
            cat_name = format_category_name(category)
            pct = stats['percentage']
            print(f"  {cat_name}: {stats['earned_points']}/{stats['total_points']} points ({pct:.0f}%)")

        print()


def run_exam_mode():
    """
    Run exam mode (convenience function).

    Returns:
        ExamResult: Exam result or None if cancelled
    """
    session = ExamSession()
    session.start()

    if not session.tasks:
        return None

    # Wait for user to complete tasks
    input("\nPress Enter when you're ready to validate your work...")

    # Validate
    result = session.validate_all()

    return result
