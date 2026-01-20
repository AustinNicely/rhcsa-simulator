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
            fmt.print_menu_option(6, "Scenario Mode", "Multi-step real-world scenarios [NEW]")
            fmt.print_menu_option(7, "Troubleshooting", "Diagnose & fix broken systems [NEW]")
            print()
            print(fmt.dim("=== Progress & Analytics ==="))
            fmt.print_menu_option(8, "View Progress", "See your exam history and statistics")
            fmt.print_menu_option(9, "Weak Areas", "Analyze weak spots & get recommendations [NEW]")
            fmt.print_menu_option(10, "Bookmarks", "Manage saved tasks for later [NEW]")
            fmt.print_menu_option(11, "Export Report", "Generate PDF/HTML progress report [NEW]")
            print()
            print(fmt.dim("=== Help & Info ==="))
            fmt.print_menu_option(12, "Task Statistics", "View available tasks by category")
            fmt.print_menu_option(13, "Help", "How to use this simulator")
            fmt.print_menu_option(0, "Exit", "Quit the simulator")
            print()

            choice = input("Select an option: ").strip()

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
                return 'scenario'
            elif choice == '7':
                return 'troubleshoot'
            elif choice == '8':
                return 'progress'
            elif choice == '9':
                return 'weak_areas'
            elif choice == '10':
                return 'bookmarks'
            elif choice == '11':
                return 'export'
            elif choice == '12':
                return 'stats'
            elif choice == '13':
                return 'help'
            elif choice == '0':
                return 'exit'
            else:
                print(fmt.error("Invalid selection."))
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

    def show_weak_areas(self):
        """Show weak areas analysis and recommendations."""
        from core.bookmarks import get_weak_area_analyzer

        fmt.clear_screen()
        fmt.print_header("WEAK AREA ANALYSIS")

        analyzer = get_weak_area_analyzer()
        report = analyzer.get_summary_report()

        # Overall stats
        print(fmt.bold("Overall Performance:"))
        print(f"  Total Attempts: {report['total_attempts']}")
        print(f"  Success Rate: {report['overall_success_rate']*100:.1f}%")
        print(f"  Score Rate: {report['overall_score_rate']*100:.1f}%")
        print(f"  Categories Practiced: {report['categories_practiced']}")
        print()

        # Weak areas
        if report['weak_categories']:
            fmt.print_weak_area_summary(report['weak_categories'])
        else:
            print(fmt.success("No significant weak areas detected!"))
            print("Keep practicing to gather more data.")

        print()

        # Recommendations
        if report['recommendations']:
            print(fmt.bold("Recommendations:"))
            for rec in report['recommendations']:
                fmt.print_recommendation_card(rec)

        print()
        input("Press Enter to return to menu...")

    def show_bookmarks(self):
        """Show and manage bookmarks."""
        from core.bookmarks import get_bookmark_manager

        fmt.clear_screen()
        fmt.print_header("BOOKMARKS")

        manager = get_bookmark_manager()
        bookmarks = manager.get_all()

        if not bookmarks:
            print("No bookmarks saved yet.")
            print()
            print("You can bookmark tasks during practice sessions")
            print("to revisit them later.")
        else:
            print(fmt.bold(f"Saved Bookmarks ({len(bookmarks)}):"))
            print()

            for i, bm in enumerate(bookmarks, 1):
                print(f"  {fmt.bold(str(i) + '.')} {bm.task_id}")
                print(f"      Category: {fmt.format_category_name(bm.category)}")
                print(f"      Difficulty: {fmt.format_difficulty(bm.difficulty)}")
                if bm.note:
                    print(f"      Note: {fmt.dim(bm.note)}")
                print()

            # Options
            print()
            print("Options:")
            print("  C - Clear all bookmarks")
            print("  R - Return to menu")
            print()

            choice = input("Select option: ").strip().lower()
            if choice == 'c':
                from utils.helpers import confirm_action
                if confirm_action("Clear all bookmarks?", default=False):
                    manager.clear()
                    print(fmt.success("Bookmarks cleared."))

        print()
        input("Press Enter to return to menu...")

    def export_report(self):
        """Export progress report."""
        from core.export import get_report_generator
        from core.bookmarks import get_weak_area_analyzer
        from core.mistakes_tracker import get_mistakes_tracker

        fmt.clear_screen()
        fmt.print_header("EXPORT REPORT")

        print("Generate a progress report in various formats.")
        print()
        print("Available formats:")
        print("  1. Text file (.txt)")
        print("  2. HTML file (.html)")
        print("  3. PDF file (.pdf) - requires reportlab")
        print("  4. Cancel")
        print()

        choice = input("Select format [1-4]: ").strip()

        if choice == '4':
            return

        format_map = {'1': 'text', '2': 'html', '3': 'pdf'}
        if choice not in format_map:
            print(fmt.error("Invalid selection"))
            input("Press Enter to continue...")
            return

        fmt_choice = format_map[choice]

        print()
        print("Generating report...")

        try:
            generator = get_report_generator()
            analyzer = get_weak_area_analyzer()
            tracker = get_mistakes_tracker()

            perf_data = analyzer.get_summary_report()
            mistakes_data = {'patterns': tracker.get_mistake_patterns()}

            filepath = generator.generate_progress_report(
                perf_data, mistakes_data, format=fmt_choice
            )

            print()
            print(fmt.success(f"Report generated successfully!"))
            print(f"  Location: {filepath}")
        except Exception as e:
            print()
            print(fmt.error(f"Error generating report: {e}"))

        print()
        input("Press Enter to return to menu...")
