"""
AI-Powered Feedback Agent using Claude API.
Provides intelligent, contextual feedback on RHCSA task attempts.
"""

import os
import logging
from typing import Dict, List, Optional
from core.validator import ValidationResult
from core.command_analyzer import CommandHistoryAnalyzer


logger = logging.getLogger(__name__)


class AIFeedbackAgent:
    """
    AI agent that provides intelligent feedback on task attempts.
    Uses Claude API to analyze commands, system state, and validation results.
    """

    def __init__(self):
        """Initialize AI feedback agent."""
        self.api_key = None
        self.client = None
        self.command_analyzer = CommandHistoryAnalyzer()
        self._initialize_api()

    def _initialize_api(self):
        """Initialize Claude API client."""
        # Check for API key in environment
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set. AI feedback will be disabled.")
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("AI feedback agent initialized successfully")
        except ImportError:
            logger.warning("anthropic package not installed. Install with: pip install anthropic")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if AI feedback is available."""
        return self.client is not None

    def analyze_attempt(
        self,
        task_description: str,
        task_hints: List[str],
        validation_result: ValidationResult,
        commands_used: List[Dict]
    ) -> str:
        """
        Analyze a task attempt and provide intelligent feedback.

        Args:
            task_description: The task requirements
            task_hints: Available hints for the task
            validation_result: Validation results
            commands_used: Commands executed during attempt

        Returns:
            str: AI-generated feedback
        """
        if not self.is_available():
            return self._fallback_feedback(validation_result)

        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                task_description,
                task_hints,
                validation_result,
                commands_used
            )

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            feedback = response.content[0].text
            return feedback

        except Exception as e:
            logger.error(f"AI feedback generation failed: {e}")
            return self._fallback_feedback(validation_result)

    def explain_failure(
        self,
        check_name: str,
        check_message: str,
        task_context: str,
        commands_used: List[Dict]
    ) -> str:
        """
        Explain WHY a specific validation check failed.

        Args:
            check_name: Name of the failed check
            check_message: Failure message
            task_context: Task description and requirements
            commands_used: Commands executed

        Returns:
            str: Explanation of the failure
        """
        if not self.is_available():
            return f"Check failed: {check_message}"

        try:
            prompt = f"""You are an RHCSA exam tutor. A student failed a validation check and needs to understand WHY.

Task Context:
{task_context}

Failed Check: {check_name}
Failure Message: {check_message}

Commands the student used:
{self._format_commands(commands_used)}

Explain in 2-3 sentences:
1. What specifically went wrong
2. Why it matters for RHCSA
3. What they should do to fix it

Be concise, specific, and educational. Focus on the root cause, not just symptoms."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Failed to explain failure: {e}")
            return f"Check failed: {check_message}"

    def suggest_next_step(
        self,
        task_description: str,
        current_state: str,
        commands_so_far: List[Dict]
    ) -> str:
        """
        Suggest the next logical step based on current progress.

        Args:
            task_description: What needs to be accomplished
            current_state: Current system state description
            commands_so_far: Commands executed so far

        Returns:
            str: Suggested next step
        """
        if not self.is_available():
            return "Continue working on the task and validate when ready."

        try:
            prompt = f"""You are an RHCSA exam tutor helping a student work through a task step-by-step.

Task Requirements:
{task_description}

Commands executed so far:
{self._format_commands(commands_so_far)}

Current System State:
{current_state}

Suggest the NEXT logical step they should take. Be specific about:
1. What command or action to perform next
2. Why this step is needed
3. What they should verify after

Keep it concise (2-3 sentences). Don't give away the entire solution, just the next step."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=384,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Failed to suggest next step: {e}")
            return "Continue working on the task requirements."

    def compare_approaches(
        self,
        task_description: str,
        user_commands: List[Dict],
        optimal_commands: List[str],
        validation_result: ValidationResult
    ) -> str:
        """
        Compare user's approach to optimal solution.

        Args:
            task_description: Task requirements
            user_commands: Commands user executed
            optimal_commands: Optimal command sequence
            validation_result: Result of validation

        Returns:
            str: Comparison and recommendations
        """
        if not self.is_available():
            return "Task validation complete."

        try:
            prompt = f"""You are an RHCSA exam tutor analyzing how a student solved a task.

Task: {task_description}

Student's Commands:
{self._format_commands(user_commands)}

Task Hints (educational guidance, NOT commands to execute or expand):
{chr(10).join(f"  {i+1}. {hint}" for i, hint in enumerate(optimal_commands))}

IMPORTANT: The hints above are educational text only. Do NOT execute, expand, or show help output for any commands mentioned in the hints.

Validation Result:
- Passed: {validation_result.passed}
- Score: {validation_result.score}/{validation_result.max_points}

Provide brief feedback on:
1. What they did well
2. What could be improved or done more efficiently
3. Any RHCSA exam tips related to this approach

Keep it encouraging and educational (3-4 sentences)."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Failed to compare approaches: {e}")
            return "Task completed."

    def _build_analysis_prompt(
        self,
        task_description: str,
        task_hints: List[str],
        validation_result: ValidationResult,
        commands_used: List[Dict]
    ) -> str:
        """Build comprehensive analysis prompt for Claude."""

        # Format validation checks
        checks_summary = []
        for check in validation_result.checks:
            status = "✓ PASS" if check.passed else "✗ FAIL"
            checks_summary.append(f"  {status} {check.name}: {check.message} ({check.points}/{check.points if check.passed else validation_result.max_points} points)")

        prompt = f"""You are an expert RHCSA exam tutor analyzing a student's task attempt. Provide detailed, actionable feedback.

TASK REQUIREMENTS:
{task_description}

VALIDATION RESULTS:
Overall: {'PASSED' if validation_result.passed else 'FAILED'}
Score: {validation_result.score}/{validation_result.max_points} points

Individual Checks:
{chr(10).join(checks_summary)}

COMMANDS EXECUTED:
{self._format_commands(commands_used)}

AVAILABLE HINTS (not shown to student yet):
{chr(10).join(f"  {i+1}. {hint}" for i, hint in enumerate(task_hints[:3]))}

Provide feedback in this format:

**What Went Wrong:**
[Explain specifically what checks failed and why]

**Root Cause:**
[Identify the underlying issue - wrong command, missing step, incorrect syntax, etc.]

**How to Fix:**
[Specific steps to correct the issue, referencing the commands they should run]

**RHCSA Exam Tip:**
[One quick tip relevant to this task type]

Be concise but thorough. Focus on teaching, not just telling the answer."""

        return prompt

    def _format_commands(self, commands: List[Dict]) -> str:
        """Format command list for display."""
        if not commands:
            return "  (No commands recorded)"

        lines = []
        for cmd in commands:
            category = cmd.get('category', 'unknown')
            command = cmd.get('command', '')
            lines.append(f"  {cmd.get('sequence', '?')}. {command} [{category}]")

        return "\n".join(lines)

    def _fallback_feedback(self, validation_result: ValidationResult) -> str:
        """Provide basic feedback when AI is unavailable."""
        if validation_result.passed:
            return "✓ Task completed successfully! All validation checks passed."

        feedback_lines = ["Task validation failed. Here's what went wrong:\n"]

        for check in validation_result.checks:
            if not check.passed:
                feedback_lines.append(f"  ✗ {check.name}: {check.message}")

        feedback_lines.append("\nReview the hints and try again.")

        return "\n".join(feedback_lines)

    def get_learning_insight(self, category: str, task_pattern: str) -> Optional[str]:
        """
        Get a learning insight for a category/task pattern.

        Args:
            category: Task category (e.g., 'networking', 'lvm')
            task_pattern: Type of task (e.g., 'static_ip', 'create_vg')

        Returns:
            str: Learning insight or None
        """
        if not self.is_available():
            return None

        try:
            prompt = f"""You are an RHCSA exam tutor. Provide a quick learning insight for this topic.

Category: {category}
Task Type: {task_pattern}

Give ONE important exam tip or common mistake to avoid for this type of task.
Keep it to 1-2 sentences. Be specific and practical."""

            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use Haiku for quick insights
                max_tokens=128,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.debug(f"Could not get learning insight: {e}")
            return None


# Global instance
_ai_agent = None


def get_ai_agent() -> AIFeedbackAgent:
    """Get or create global AI feedback agent instance."""
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = AIFeedbackAgent()
    return _ai_agent
