"""
Base task class for all RHCSA exam tasks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)


class BaseTask(ABC):
    """
    Abstract base class for all RHCSA exam tasks.

    All task categories must inherit from this class and implement
    the generate() and validate() methods.
    """

    def __init__(self, id, category, difficulty, points):
        """
        Initialize base task.

        Args:
            id (str): Unique task ID
            category (str): Task category
            difficulty (str): Difficulty level ('easy', 'exam', 'hard')
            points (int): Maximum points for this task
        """
        self.id = id
        self.category = category
        self.difficulty = difficulty
        self.points = points
        self.description = ""
        self.hints = []
        self.params = {}

    @abstractmethod
    def generate(self, **params):
        """
        Generate task with randomized parameters.

        This method should:
        1. Accept optional parameters
        2. Generate random values for task (usernames, sizes, etc.)
        3. Set self.description with the task description
        4. Set self.hints with helpful hints
        5. Return self for method chaining

        Args:
            **params: Optional parameters to customize generation

        Returns:
            BaseTask: self for method chaining
        """
        pass

    @abstractmethod
    def validate(self):
        """
        Validate task completion by checking system state.

        This method should:
        1. Use validators to check if task was completed correctly
        2. Create ValidationCheck objects for each check
        3. Calculate points earned
        4. Return ValidationResult

        Returns:
            ValidationResult: Result of validation
        """
        pass

    def get_description(self):
        """
        Get task description.

        Returns:
            str: Task description
        """
        return self.description

    def get_hints(self):
        """
        Get list of hints for the task.

        Returns:
            list: List of hint strings
        """
        return self.hints

    def get_category_display_name(self):
        """
        Get formatted category name.

        Returns:
            str: Formatted category name
        """
        from utils.formatters import format_category_name
        return format_category_name(self.category)

    def get_difficulty_display(self):
        """
        Get formatted difficulty level.

        Returns:
            str: Formatted difficulty
        """
        from utils.formatters import format_difficulty
        return format_difficulty(self.difficulty)

    def to_dict(self):
        """
        Convert task to dictionary.

        Returns:
            dict: Task data
        """
        return {
            'id': self.id,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'description': self.description,
            'hints': self.hints
        }

    def __repr__(self):
        """String representation of task."""
        return f"<Task {self.id}: {self.category} ({self.difficulty}, {self.points}pts)>"


class SimpleTask(BaseTask):
    """
    Simple task implementation for quick task creation.

    This class provides a non-abstract implementation that can be used
    for simple tasks without creating a new class.
    """

    def __init__(self, id, category, difficulty, points, description="", validation_func=None):
        """
        Initialize simple task.

        Args:
            id (str): Task ID
            category (str): Category
            difficulty (str): Difficulty
            points (int): Points
            description (str): Task description
            validation_func (callable): Function that returns ValidationResult
        """
        super().__init__(id, category, difficulty, points)
        self.description = description
        self._validation_func = validation_func

    def generate(self, **params):
        """Generate task (already configured)."""
        return self

    def validate(self):
        """Validate using provided function."""
        if self._validation_func:
            return self._validation_func()

        # Default: return failed result
        from core.validator import ValidationResult
        return ValidationResult(
            task_id=self.id,
            passed=False,
            score=0,
            max_score=self.points,
            error_message="No validation function provided"
        )
