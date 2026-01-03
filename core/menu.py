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
            print(fmt.dim("=== Learning Modes ==="))
            fmt.print_menu_option(1, "Learn Mode", "Study RHCSA concepts with explanations & examples")
            fmt.print_menu_option(2, "Guided Practice", "Practice with progressive hints & feedback")
            fmt.print_menu_option(3, "Command Recall", "Build muscle memory by typing commands")
            print()
            print(fmt.dim("=== Testing Modes ==="))
            fmt.print_menu_option(4, "Exam Mode", "Take a full mock RHCSA exam (15-20 tasks)")
            fmt.print_menu_option(5, "Practice Mode", "Practice specific task categories")
            print()
            print(fmt.dim("=== Progress & Help ==="))
            fmt.print_menu_option(6, "View Progress", "See your exam history and statistics")
            fmt.print_menu_option(7, "Task Statistics", "View available tasks by category")
            fmt.print_menu_option(8, "Help", "How to use this simulator")
            fmt.print_menu_option(9, "Exit", "Quit the simulator")
            print()

            choice = input("Select an option [1-9]: ").strip()

            if choice == '1':
                return 'learn'
            elif choice == '2':
                return 'guided_practice'
            elif choice == '3':
                return 'command_recall'
            elif choice == '4':
                return 'exam'
            elif choice == '5':
                return 'practice'
            elif choice == '6':
                return 'progress'
            elif choice == '7':
                return 'stats'
            elif choice == '8':
                return 'help'
            elif choice == '9':
                return 'exit'
            else:
                print(fmt.error("Invalid selection. Please choose 1-9."))
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

=== LEARNING MODES ===

1. LEARN MODE
   - Study RHCSA concepts with detailed explanations
   - See command syntax, examples, and common flags
   - Learn common mistakes to avoid
   - Review exam-specific tricks and tips
   - Best for: First-time learners, reviewing unfamiliar topics

2. GUIDED PRACTICE
   - Practice tasks with progressive 3-level hints
   - Level 1: Concept reminder
   - Level 2: Command structure and syntax
   - Level 3: Full solution with examples
   - Get adaptive feedback explaining failures
   - Best for: Building confidence, learning proper approach

3. COMMAND RECALL TRAINING
   - Build muscle memory by typing commands
   - Type the command before running it on your system
   - Get instant feedback on command accuracy
   - Track your command recall accuracy
   - Best for: Memorizing commands, building speed

=== TESTING MODES ===

4. EXAM MODE
   - Simulates a real RHCSA exam with 15-20 tasks
   - Tasks cover all RHCSA objectives
   - Optional 2.5-hour timer
   - Complete tasks on your Linux system
   - Return to validate your work
   - Results are saved and tracked over time

5. PRACTICE MODE
   - Practice specific categories without hints
   - Choose difficulty level (easy/exam/hard)
   - Get immediate pass/fail feedback
   - Test your knowledge without assistance

=== PROGRESS & HELP ===

6. VIEW PROGRESS
   - See your exam history
   - Track score trends over time
   - View pass rates and statistics

7. TASK STATISTICS
   - See all available tasks by category
   - Check task counts and coverage

=== IMPORTANT NOTES ===

- You must run this as root (sudo)
- This tool VALIDATES your work - it doesn't make changes
- All validation commands are read-only and safe
- Complete tasks on your actual Linux system
- You can validate multiple times during an exam

=== RECOMMENDED LEARNING PATH ===

1. Start with LEARN MODE for each topic
2. Practice with GUIDED PRACTICE (use hints as needed)
3. Build speed with COMMAND RECALL TRAINING
4. Test yourself with PRACTICE MODE (no hints)
5. Take full EXAM MODE when confident

=== CATEGORIES COVERED ===

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
