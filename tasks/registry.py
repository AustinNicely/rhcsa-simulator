"""
Task registry system for RHCSA Simulator.
Provides decorator-based task registration and retrieval.
"""

import random
import logging
from collections import defaultdict
from typing import List, Optional
from config import settings


logger = logging.getLogger(__name__)


class TaskRegistry:
    """
    Central registry for all task classes.

    Uses singleton pattern with decorator-based registration.
    """

    _instance = None
    _tasks = defaultdict(list)  # category -> list of task classes
    _initialized = False

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, category):
        """
        Decorator to register task classes.

        Usage:
            @TaskRegistry.register("users_groups")
            class CreateUserTask(BaseTask):
                ...

        Args:
            category (str): Task category

        Returns:
            function: Decorator function
        """
        def wrapper(task_class):
            cls._tasks[category].append(task_class)
            logger.debug(f"Registered task: {task_class.__name__} in category {category}")
            return task_class
        return wrapper

    @classmethod
    def get_all_categories(cls):
        """
        Get list of all registered categories.

        Returns:
            list: List of category names
        """
        return list(cls._tasks.keys())

    @classmethod
    def get_tasks_by_category(cls, category):
        """
        Get all task classes for a category.

        Args:
            category (str): Category name

        Returns:
            list: List of task classes
        """
        return cls._tasks.get(category, [])

    @classmethod
    def get_task_count(cls, category=None):
        """
        Get count of registered tasks.

        Args:
            category (str): Optional category to filter

        Returns:
            int: Number of tasks
        """
        if category:
            return len(cls._tasks.get(category, []))
        return sum(len(tasks) for tasks in cls._tasks.values())

    @classmethod
    def get_random_task(cls, category=None, difficulty=None):
        """
        Get a random task instance.

        Args:
            category (str): Optional category filter
            difficulty (str): Optional difficulty filter

        Returns:
            BaseTask: Random task instance (generated)
        """
        # Get available task classes
        if category:
            task_classes = cls._tasks.get(category, [])
        else:
            task_classes = []
            for cat_tasks in cls._tasks.values():
                task_classes.extend(cat_tasks)

        if not task_classes:
            logger.warning(f"No tasks found for category: {category}")
            return None

        # Filter by difficulty if specified
        if difficulty:
            filtered = [tc for tc in task_classes if hasattr(tc, 'difficulty') and tc.difficulty == difficulty]
            if filtered:
                task_classes = filtered

        # Select random task class
        task_class = random.choice(task_classes)

        # Instantiate and generate
        try:
            task = task_class()
            task.generate()
            return task
        except Exception as e:
            logger.error(f"Error creating task from {task_class.__name__}: {e}")
            return None

    @classmethod
    def get_random_tasks(cls, count, categories=None, difficulty=None, exclude_ids=None):
        """
        Get multiple random tasks.

        Args:
            count (int): Number of tasks to generate
            categories (list): Optional list of categories to include
            difficulty (str): Optional difficulty filter
            exclude_ids (list): Optional list of task IDs to exclude

        Returns:
            list: List of generated task instances
        """
        tasks = []
        exclude_ids = exclude_ids or []
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loop

        # Determine which categories to use
        if categories:
            available_categories = [c for c in categories if c in cls._tasks]
        else:
            available_categories = list(cls._tasks.keys())

        if not available_categories:
            logger.warning("No categories available for task generation")
            return []

        while len(tasks) < count and attempts < max_attempts:
            attempts += 1

            # Select category (round-robin for balanced distribution)
            category = available_categories[len(tasks) % len(available_categories)]

            # Get random task from category
            task = cls.get_random_task(category=category, difficulty=difficulty)

            if task and task.id not in exclude_ids:
                tasks.append(task)
                exclude_ids.append(task.id)

        if len(tasks) < count:
            logger.warning(f"Could only generate {len(tasks)} tasks out of {count} requested")

        return tasks

    @classmethod
    def get_exam_tasks(cls, count=None):
        """
        Get tasks for a full exam (exam difficulty, balanced across categories).

        Args:
            count (int): Number of tasks (default: from settings)

        Returns:
            list: List of exam tasks
        """
        if count is None:
            count = settings.DEFAULT_EXAM_TASKS

        return cls.get_random_tasks(count, difficulty="exam")

    @classmethod
    def get_practice_tasks(cls, category, difficulty="exam", count=None):
        """
        Get tasks for practice mode.

        Args:
            category (str): Category to practice
            difficulty (str): Difficulty level
            count (int): Number of tasks (default: from settings)

        Returns:
            list: List of practice tasks
        """
        if count is None:
            count = settings.DEFAULT_PRACTICE_TASKS

        return cls.get_random_tasks(count, categories=[category], difficulty=difficulty)

    @classmethod
    def initialize(cls):
        """
        Initialize task registry by importing all task modules.

        This ensures all task classes are registered.
        """
        if cls._initialized:
            return

        logger.info("Initializing task registry...")

        # Import all task modules to trigger registration
        task_modules = [
            'tasks.users_groups',
            'tasks.permissions',
            'tasks.lvm',
            'tasks.filesystems',
            'tasks.networking',
            'tasks.selinux',
            'tasks.services',
            'tasks.essential_tools',
            'tasks.boot',
            'tasks.processes',
            'tasks.scheduling',
            'tasks.containers'
        ]

        for module_name in task_modules:
            try:
                __import__(module_name)
                logger.debug(f"Imported {module_name}")
            except ImportError as e:
                logger.warning(f"Could not import {module_name}: {e}")
            except Exception as e:
                logger.error(f"Error importing {module_name}: {e}")

        cls._initialized = True
        logger.info(f"Task registry initialized with {cls.get_task_count()} tasks across {len(cls.get_all_categories())} categories")

    @classmethod
    def print_statistics(cls):
        """Print task registry statistics."""
        print("\nTask Registry Statistics:")
        print("=" * 50)
        print(f"Total categories: {len(cls.get_all_categories())}")
        print(f"Total tasks: {cls.get_task_count()}")
        print("\nTasks by category:")

        for category in sorted(cls.get_all_categories()):
            count = cls.get_task_count(category)
            from utils.formatters import format_category_name
            print(f"  {format_category_name(category)}: {count} tasks")


# Create global instance
_registry = TaskRegistry()


def get_registry():
    """
    Get global TaskRegistry instance.

    Returns:
        TaskRegistry: Global registry
    """
    return _registry
