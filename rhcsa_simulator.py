#!/usr/bin/env python3
"""
RHCSA Mock Exam Simulator - Main Entry Point

A realistic RHCSA exam simulator that generates tasks, validates system state,
and tracks progress over time.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import require_root
from utils.logging import setup_logging
from core.menu import MenuSystem
from core.exam import run_exam_mode
from core.practice import run_practice_mode
from core.practice_enhanced import run_guided_practice
from core.learn import run_learn_mode
from core.command_recall import run_command_recall
from core.results import get_results_manager
from core.scenario_mode import run_scenario_mode
from core.troubleshoot_mode import run_troubleshoot_mode
from config import settings


def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check root privileges
    try:
        require_root()
    except SystemExit:
        return 1

    # Initialize menu system
    menu = MenuSystem()

    # Main loop
    while True:
        try:
            choice = menu.display_main_menu()

            if choice == 'learn':
                run_learn_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'guided_practice':
                run_guided_practice()
                input("\nPress Enter to return to menu...")

            elif choice == 'command_recall':
                run_command_recall()
                input("\nPress Enter to return to menu...")

            elif choice == 'exam':
                run_exam_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'practice':
                run_practice_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'scenario':
                run_scenario_mode()

            elif choice == 'troubleshoot':
                run_troubleshoot_mode()

            elif choice == 'progress':
                results_mgr = get_results_manager()
                results_mgr.display_progress()
                input("\nPress Enter to return to menu...")

            elif choice == 'weak_areas':
                menu.show_weak_areas()

            elif choice == 'bookmarks':
                menu.show_bookmarks()

            elif choice == 'export':
                menu.export_report()

            elif choice == 'stats':
                menu.show_stats()

            elif choice == 'setup_disks':
                menu.setup_practice_disks()

            elif choice == 'help':
                menu.show_help()

            elif choice == 'exit':
                print("\nThank you for using RHCSA Mock Exam Simulator!")
                print("Good luck with your certification!")
                return 0

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            confirm = input("Are you sure you want to exit? [y/N]: ").strip().lower()
            if confirm in ['y', 'yes']:
                return 0

        except Exception as e:
            logger.exception("Unexpected error in main loop")
            print(f"\nError: {e}")
            print("Please report this issue if it persists.")
            input("Press Enter to return to menu...")


if __name__ == '__main__':
    sys.exit(main())
