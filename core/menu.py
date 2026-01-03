"""
Main menu system for RHCSA Simulator.
"""

import sys
from utils import formatters as fmt
from config import settings


class MenuSystem:
    """
    Main menu system for the application.
    """

    def __init__(self):
        """Initialize menu system."""
        pass

    def display_main_menu(self):
        """Display main menu and get selection."""
        while True:
            fmt.clear_screen()
            self._print_header()

            print(fmt.bold("Main Menu:"))
            print()
            fmt.print_menu_option(1, "Exam Mode", "Take a full mock RHCSA exam (15-20 tasks)")
            fmt.print_menu_option(2, "Practice Mode", "Practice specific task categories")
            fmt.print_menu_option(3, "View Progress", "See your exam history and statistics")
            fmt.print_menu_option(4, "Task Statistics", "View available tasks by category")
            fmt.print_menu_option(5, "Help", "How to use this simulator")
            fmt.print_menu_option(6, "Exit", "Quit the simulator")
            print()

            choice = input("Select an option [1-6]: ").strip()

            if choice == '1':
                return 'exam'
            elif choice == '2':
                return 'practice'
            elif choice == '3':
                return 'progress'
            elif choice == '4':
                return 'stats'
            elif choice == '5':
                return 'help'
            elif choice == '6':
                return 'exit'
            else:
                print(fmt.error("Invalid selection. Please choose 1-6."))
                input("Press Enter to continue...")

    def _print_header(self):
        """Print application header."""
        fmt.print_header(f"{settings.APP_NAME} v{settings.VERSION}")

    def show_help(self):
        """Display help information."""
        fmt.clear_screen()
        fmt.print_header("HELP")

        help_text = """
RHCSA Mock Exam Simulator - How to Use

1. EXAM MODE
   - Simulates a real RHCSA exam with 15-20 tasks
   - Tasks cover all RHCSA objectives
   - Optional 2.5-hour timer
   - Complete tasks on your Linux system
   - Return to validate your work
   - Results are saved and tracked over time

2. PRACTICE MODE
   - Practice specific categories (users, LVM, SELinux, etc.)
   - Choose difficulty level (easy/exam/hard)
   - Get immediate feedback after each task
   - See hints if you need help

3. VIEW PROGRESS
   - See your exam history
   - Track score trends over time
   - View pass rates and statistics

4. IMPORTANT NOTES
   - You must run this as root (sudo)
   - This tool VALIDATES your work - it doesn't make changes
   - All validation commands are read-only and safe
   - Complete tasks on your actual Linux system
   - You can validate multiple times during an exam

5. EXAM PREPARATION TIPS
   - Practice each category individually first
   - Take multiple full exams to build confidence
   - Review failed tasks to understand mistakes
   - Real RHCSA exam allows access to documentation
   - Focus on understanding, not memorization

6. CATEGORIES COVERED
   - Users & Groups Management
   - File Permissions & ACLs
   - LVM (Logical Volume Management)
   - File Systems
   - Networking
   - SELinux
   - Services (systemd)
   - Boot Targets
   - Process Management
   - Task Scheduling
   - Containers (Podman)
   - Essential Tools

For more information, visit: https://www.redhat.com/rhcsa
        """

        print(help_text)
        input("\nPress Enter to return to menu...")

    def show_stats(self):
        """Show task statistics."""
        from tasks.registry import TaskRegistry

        fmt.clear_screen()
        fmt.print_header("TASK STATISTICS")

        # Initialize registry
        TaskRegistry.initialize()

        # Print statistics
        TaskRegistry.print_statistics()

        print()
        input("Press Enter to return to menu...")
