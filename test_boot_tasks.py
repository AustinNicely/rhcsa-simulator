#!/usr/bin/env python3
"""Test script to verify boot tasks are properly implemented."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the boot module
    from tasks import boot
    from tasks.registry import TaskRegistry

    print("Successfully imported boot tasks module!")
    print()

    # Get all boot tasks from registry
    boot_tasks = TaskRegistry.get_tasks_by_category("boot")

    print(f"Found {len(boot_tasks)} boot task classes:")
    print()

    for task_class in boot_tasks:
        task = task_class()
        print(f"  - {task_class.__name__}")
        print(f"    ID: {task.id}")
        print(f"    Difficulty: {task.difficulty}")
        print(f"    Points: {task.points}")

        # Test generate method
        task.generate()
        print(f"    Description: {task.description[:80]}...")
        print(f"    Hints: {len(task.hints)} hints available")
        print()

    print("All boot tasks loaded successfully!")

except Exception as e:
    print(f"Error loading boot tasks: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
