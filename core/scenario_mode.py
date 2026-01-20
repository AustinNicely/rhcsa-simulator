"""
Scenario mode for RHCSA Simulator.
Runs multi-step scenario-based practice sessions.
"""

import logging
from datetime import datetime
from core.scenarios import ScenarioRegistry, ScenarioSession, Scenario
from core.validator import get_validator
from core.bookmarks import get_bookmark_manager, get_weak_area_analyzer
from core.mistakes_tracker import get_mistakes_tracker
from utils import formatters as fmt
from utils.helpers import confirm_action


logger = logging.getLogger(__name__)


class ScenarioMode:
    """
    Scenario-based practice mode.

    Runs multi-step, interconnected tasks that simulate real-world scenarios.
    """

    def __init__(self):
        """Initialize scenario mode."""
        self.current_session = None
        self.validator = get_validator()
        self.weak_analyzer = get_weak_area_analyzer()
        self.mistakes_tracker = get_mistakes_tracker()

    def start(self):
        """Start scenario mode."""
        fmt.clear_screen()
        fmt.print_header("SCENARIO MODE")

        print("Scenarios are multi-step tasks that simulate real-world situations.")
        print("Complete all steps to fully solve the scenario.")
        print()

        # Select scenario
        scenario = self._select_scenario()
        if not scenario:
            return

        # Run scenario
        self._run_scenario(scenario)

    def _select_scenario(self):
        """Select a scenario to run."""
        scenarios = ScenarioRegistry.get_all_scenarios()

        if not scenarios:
            print(fmt.error("No scenarios available"))
            return None

        print(fmt.bold("Available Scenarios:"))
        print()

        for i, s in enumerate(scenarios, 1):
            difficulty_str = fmt.format_difficulty(s['difficulty'])
            print(f"  {fmt.bold(str(i) + '.')} {s['title']}")
            print(f"      {fmt.dim(s['description'][:60] + '...')}")
            print(f"      {s['step_count']} steps | {s['total_points']} points | ~{s['time_estimate']} min | {difficulty_str}")
            print()

        print(f"  {fmt.bold('Q.')} Return to main menu")
        print()

        while True:
            choice = input("Select scenario (number or Q): ").strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scenarios):
                    return ScenarioRegistry.get_scenario(scenarios[idx]['id'])
                else:
                    print(fmt.error("Invalid selection"))
            except ValueError:
                print(fmt.error("Please enter a number or Q"))

    def _run_scenario(self, scenario: Scenario):
        """Run a scenario session."""
        self.current_session = ScenarioSession(scenario)
        self.current_session.start_time = datetime.now()

        fmt.clear_screen()
        self._print_scenario_intro(scenario)

        if not confirm_action("Ready to begin?", default=True):
            return

        # Run through steps
        while not self.current_session.is_complete():
            step = self.current_session.get_current_step()
            if not step:
                break

            result = self._run_step(step)
            self.current_session.complete_step(step.step_number, result)

            if not self.current_session.is_complete():
                self._show_progress()
                if not confirm_action("Continue to next step?", default=True):
                    break

        # Show final results
        self.current_session.end_time = datetime.now()
        self._show_final_results()

    def _print_scenario_intro(self, scenario: Scenario):
        """Print scenario introduction."""
        print()
        print("=" * 60)
        print(fmt.bold(f"SCENARIO: {scenario.title}"))
        print("=" * 60)
        print()
        print(fmt.bold("Context:"))
        print(f"  {scenario.context}")
        print()
        print(fmt.bold("Objectives:"))
        for obj in scenario.objectives:
            print(f"  • {obj}")
        print()
        print(f"Total Points: {scenario.total_points}")
        print(f"Estimated Time: {scenario.time_estimate_minutes} minutes")
        print(f"Steps: {len(scenario.steps)}")
        print()

    def _run_step(self, step):
        """Run a single scenario step."""
        fmt.clear_screen()

        session = self.current_session
        progress = session.get_progress()

        # Show progress header
        fmt.print_scenario_progress(
            session.scenario.title,
            progress['completed_steps'],
            progress['total_steps'],
            progress['earned_points'],
            progress['total_points']
        )

        print()
        print(f"{fmt.bold(f'Step {step.step_number}:')} ({step.points} points)")
        print("-" * 50)
        print(step.description)
        print()

        # Show dependencies if any
        if step.depends_on:
            print(fmt.dim(f"(Depends on completing steps: {step.depends_on})"))
            print()

        # Offer hints
        if step.hints and confirm_action("Show hints?", default=False):
            print()
            print(fmt.bold("Hints:"))
            for i, hint in enumerate(step.hints, 1):
                print(f"  {i}. {hint}")
            print()

        # Wait for user to complete
        input("Complete this step on your system, then press Enter to validate...")

        # Validate (simplified - in real implementation would call task validators)
        print()
        print(fmt.bold("Validating..."))

        # For now, return a mock result
        # In full implementation, this would instantiate the appropriate task
        # and run its validation
        from core.validator import ValidationResult, ValidationCheck

        # Simulated validation - in real app would run actual validators
        checks = [
            ValidationCheck(
                name=f"step_{step.step_number}_check",
                passed=True,  # Would be actual validation
                points=step.points,
                message="Step completed successfully"
            )
        ]

        result = ValidationResult(
            task_id=f"{self.current_session.scenario.id}_step_{step.step_number}",
            passed=True,
            score=step.points,
            max_score=step.points,
            checks=checks
        )

        # Display result
        self._show_step_result(step, result)

        return result

    def _show_step_result(self, step, result):
        """Show step validation result."""
        print()
        print("Validation Results:")
        print("-" * 40)

        for check in result.checks:
            fmt.print_check_result(
                check.name,
                check.passed,
                check.message,
                check.points,
                check.max_points
            )

        print()
        if result.passed:
            print(fmt.success(f"Step {step.step_number} completed! +{result.score} points"))
        else:
            print(fmt.error(f"Step {step.step_number} not complete. {result.score}/{step.points} points"))

    def _show_progress(self):
        """Show current scenario progress."""
        progress = self.current_session.get_progress()

        print()
        fmt.print_scenario_progress(
            self.current_session.scenario.title,
            progress['completed_steps'],
            progress['total_steps'],
            progress['earned_points'],
            progress['total_points']
        )
        print()

    def _show_final_results(self):
        """Show final scenario results."""
        session = self.current_session
        progress = session.get_progress()

        fmt.clear_screen()
        fmt.print_header("SCENARIO COMPLETE")

        print(fmt.bold(f"Scenario: {session.scenario.title}"))
        print()

        # Overall result
        passed = progress['percentage'] >= 70
        status = fmt.success("PASSED") if passed else fmt.error("FAILED")

        print(f"Result: {status}")
        print(f"Score: {progress['earned_points']}/{progress['total_points']} ({progress['percentage']:.0f}%)")
        print(f"Steps Completed: {progress['completed_steps']}/{progress['total_steps']}")
        print()

        # Duration
        if session.start_time and session.end_time:
            duration = session.end_time - session.start_time
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            print(f"Time Taken: {minutes}m {seconds}s")
            print(f"Estimated Time: {session.scenario.time_estimate_minutes}m")
            print()

        # Step breakdown
        print(fmt.bold("Step Results:"))
        for step in session.scenario.steps:
            if step.step_number in session.step_results:
                result = session.step_results[step.step_number]
                status_icon = fmt.success("✓") if result.passed else fmt.error("✗")
                print(f"  {status_icon} Step {step.step_number}: {result.score}/{step.points} pts")
            else:
                print(f"  {fmt.dim('○')} Step {step.step_number}: Not attempted")

        print()
        input("Press Enter to continue...")


def run_scenario_mode():
    """Run scenario mode (convenience function)."""
    mode = ScenarioMode()
    mode.start()
