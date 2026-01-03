"""
Command Recall Training Mode - Practice typing commands before executing.
"""

import logging
import re
from difflib import SequenceMatcher
from tasks.registry import TaskRegistry
from utils import formatters as fmt
from utils.helpers import confirm_action
from config import settings


logger = logging.getLogger(__name__)


class CommandRecallSession:
    """
    Command recall training mode where users type commands before execution.
    Validates command syntax and structure to build muscle memory.
    """

    def __init__(self):
        """Initialize command recall session."""
        self.category = None
        self.difficulty = "exam"
        self.task_count = 5
        self.correct_commands = 0
        self.total_commands = 0
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start command recall training session."""
        # Initialize registry
        TaskRegistry.initialize()

        # Select category
        self.category = self._select_category()
        if not self.category:
            return

        # Select difficulty
        self.difficulty = self._select_difficulty()

        # Get tasks
        tasks = TaskRegistry.get_practice_tasks(
            self.category,
            self.difficulty,
            self.task_count
        )

        if not tasks:
            print(fmt.error(f"No tasks available for {self.category}"))
            return

        # Practice command recall for each task
        for i, task in enumerate(tasks, 1):
            self._practice_command_recall(task, i, len(tasks))

        # Show summary
        self._show_recall_summary()

    def _practice_command_recall(self, task, current, total):
        """
        Practice recalling commands for a single task.

        Args:
            task: The task to practice
            current: Current task number
            total: Total number of tasks
        """
        fmt.clear_screen()

        print(f"Command Recall Training - Task {current}/{total}")
        print("=" * 70)
        print()

        # Display task
        print(fmt.bold("📋 TASK:"))
        print(task.description)
        print()
        print(fmt.bold(f"Category: {fmt.format_category_name(task.category)}"))
        print(fmt.bold(f"Difficulty: {fmt.format_difficulty(task.difficulty)}"))
        print()

        # Get expected commands from hints
        expected_commands = self._extract_commands_from_task(task)

        if not expected_commands:
            print(fmt.warning("No command examples available for this task."))
            print()
            if current < total:
                input("Press Enter to continue to next task...")
            return

        print(fmt.dim("💡 Type the command(s) you would use to complete this task"))
        print(fmt.dim("   Type 'hint' to see a hint, or 'skip' to skip this task"))
        print(fmt.dim("   Type 'done' when you've entered all commands"))
        print()

        # Track commands entered
        user_commands = []
        hints_shown = 0

        while True:
            cmd_num = len(user_commands) + 1
            user_input = input(f"Command {cmd_num}> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'done':
                if not user_commands:
                    print(fmt.warning("You haven't entered any commands yet!"))
                    continue
                break

            elif user_input.lower() == 'skip':
                print(fmt.warning("Skipping task..."))
                print()
                if current < total:
                    input("Press Enter to continue to next task...")
                return

            elif user_input.lower() == 'hint':
                hints_shown += 1
                self._show_command_hint(task, hints_shown, expected_commands)
                continue

            elif user_input.lower() == 'help':
                print(fmt.info("Commands: type your command, 'hint' (get help), 'done' (finish), 'skip' (skip task)"))
                print()
                continue

            else:
                # Validate command
                user_commands.append(user_input)
                print(fmt.dim(f"  → Recorded: {user_input}"))
                print()

        # Evaluate commands
        print()
        print(fmt.bold("🔍 Evaluating your commands..."))
        print()

        self._evaluate_commands(user_commands, expected_commands, task)

        # Update stats
        self.total_commands += len(expected_commands)

        # Continue?
        if current < total:
            print()
            if not confirm_action("Continue to next task?", default=True):
                return

    def _extract_commands_from_task(self, task):
        """
        Extract expected commands from task hints.

        Returns:
            list: List of expected command patterns
        """
        commands = []

        if not task.hints:
            return commands

        # Common command patterns for different categories
        command_patterns = {
            'users_groups': [r'useradd', r'usermod', r'groupadd', r'gpasswd', r'passwd'],
            'permissions': [r'chmod', r'chown', r'chgrp', r'setfacl', r'getfacl'],
            'services': [r'systemctl\s+(start|stop|enable|disable|restart|status)'],
            'selinux': [r'semanage\s+fcontext', r'restorecon', r'setsebool', r'getsebool', r'chcon'],
            'lvm': [r'pvcreate', r'vgcreate', r'lvcreate', r'pvs', r'vgs', r'lvs'],
            'filesystems': [r'mkfs', r'mount', r'umount', r'blkid', r'lsblk'],
            'networking': [r'nmcli', r'ip\s+addr', r'ip\s+link', r'hostnamectl'],
        }

        category_patterns = command_patterns.get(task.category, [])

        # Extract commands from hints
        for hint in task.hints:
            # Look for command-like patterns in hints
            for pattern in category_patterns:
                if re.search(pattern, hint, re.IGNORECASE):
                    # Try to extract the actual command
                    match = re.search(r'`([^`]+)`', hint)
                    if match:
                        commands.append(match.group(1))
                    else:
                        # Extract command from pattern match
                        words = hint.split()
                        for i, word in enumerate(words):
                            if re.match(pattern, word, re.IGNORECASE):
                                # Get command and a few following words
                                cmd = ' '.join(words[i:min(i+5, len(words))])
                                commands.append(cmd.strip('.,;:'))
                                break

        # If no commands found, try to extract from any code-like patterns
        if not commands:
            for hint in task.hints:
                # Look for common command patterns
                if re.search(r'\b(sudo\s+)?[a-z]+\s+[/-]', hint):
                    match = re.search(r'((?:sudo\s+)?[a-z]+\s+[^\s.]+(?:\s+[^\s.]+)*)', hint)
                    if match:
                        commands.append(match.group(1))

        return commands[:3]  # Limit to first 3 commands

    def _evaluate_commands(self, user_commands, expected_commands, task):
        """
        Evaluate user's commands against expected commands.

        Args:
            user_commands: List of commands entered by user
            expected_commands: List of expected command patterns
            task: The task being evaluated
        """
        print("=" * 70)
        print(fmt.bold("📊 COMMAND EVALUATION:"))
        print("=" * 70)
        print()

        if not expected_commands:
            print(fmt.warning("No reference commands available for comparison."))
            return

        # Track matches
        matched = set()

        # Check each user command
        for i, user_cmd in enumerate(user_commands, 1):
            print(fmt.bold(f"Command {i}: {user_cmd}"))

            best_match = None
            best_score = 0

            # Find best matching expected command
            for j, expected_cmd in enumerate(expected_commands):
                if j in matched:
                    continue

                score = self._calculate_command_similarity(user_cmd, expected_cmd)
                if score > best_score:
                    best_score = score
                    best_match = j

            # Evaluate match
            if best_score > 0.7:  # Strong match
                matched.add(best_match)
                self.correct_commands += 1
                print(fmt.success(f"  ✓ Correct! ({int(best_score * 100)}% match)"))
                if best_score < 1.0:
                    print(fmt.dim(f"  Expected: {expected_commands[best_match]}"))
            elif best_score > 0.4:  # Partial match
                matched.add(best_match)
                print(fmt.warning(f"  ~ Close! ({int(best_score * 100)}% match)"))
                print(fmt.dim(f"  Expected: {expected_commands[best_match]}"))
                self._explain_command_difference(user_cmd, expected_commands[best_match])
            else:  # No match
                print(fmt.error(f"  ✗ Not quite right"))
                self._suggest_correct_command(user_cmd, expected_commands, task)

            print()

        # Check for missing commands
        if len(matched) < len(expected_commands):
            print(fmt.warning("Missing commands:"))
            for j, expected_cmd in enumerate(expected_commands):
                if j not in matched:
                    print(f"  • {expected_cmd}")
            print()

        # Overall feedback
        accuracy = (self.correct_commands / max(len(expected_commands), len(user_commands))) if expected_commands else 0

        if accuracy >= 0.9:
            print(fmt.success("🌟 Excellent command recall!"))
        elif accuracy >= 0.7:
            print(fmt.success("👍 Good job! Keep practicing!"))
        elif accuracy >= 0.5:
            print(fmt.warning("📚 Getting there! Review the commands and try again."))
        else:
            print(fmt.warning("📖 Keep studying! Focus on command syntax and structure."))

        print("=" * 70)

    def _calculate_command_similarity(self, user_cmd, expected_cmd):
        """
        Calculate similarity between user command and expected command.

        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        # Normalize commands
        user_norm = user_cmd.lower().strip()
        expected_norm = expected_cmd.lower().strip()

        # Exact match
        if user_norm == expected_norm:
            return 1.0

        # Check if base command matches
        user_base = user_norm.split()[0]
        expected_base = expected_norm.split()[0]

        if user_base != expected_base:
            # Different base command - very low score
            return SequenceMatcher(None, user_norm, expected_norm).ratio() * 0.3

        # Same base command - check arguments
        base_score = 0.5  # 50% for matching base command

        # Compare arguments
        user_args = set(user_norm.split()[1:])
        expected_args = set(expected_norm.split()[1:])

        if not expected_args:
            arg_score = 0.5
        else:
            common_args = user_args & expected_args
            arg_score = len(common_args) / len(expected_args)

        # Combined score
        return base_score + (arg_score * 0.5)

    def _explain_command_difference(self, user_cmd, expected_cmd):
        """Explain the difference between user and expected command."""
        user_parts = user_cmd.split()
        expected_parts = expected_cmd.split()

        # Check for missing flags/arguments
        expected_set = set(expected_parts[1:])
        user_set = set(user_parts[1:])

        missing = expected_set - user_set
        extra = user_set - expected_set

        if missing:
            print(fmt.dim(f"  Missing: {' '.join(missing)}"))
        if extra:
            print(fmt.dim(f"  Extra: {' '.join(extra)}"))

    def _suggest_correct_command(self, user_cmd, expected_commands, task):
        """Suggest the correct command based on task category."""
        print(fmt.dim(f"  💡 Hint: This is a {task.category} task"))

        if expected_commands:
            print(fmt.dim(f"  Try a command like: {expected_commands[0]}"))

    def _show_command_hint(self, task, hint_level, expected_commands):
        """Show progressive hints about the command."""
        print()
        print(fmt.warning(f"━━━ HINT {hint_level} ━━━"))

        if hint_level == 1:
            # Hint 1: Command category
            print(fmt.bold("💭 Command Category:"))
            category_hints = {
                'users_groups': "User and group management commands (useradd, usermod, groupadd)",
                'permissions': "Permission and ACL commands (chmod, chown, setfacl)",
                'services': "Systemd service commands (systemctl)",
                'selinux': "SELinux commands (semanage, restorecon, setsebool)",
                'lvm': "LVM commands (pvcreate, vgcreate, lvcreate)",
                'filesystems': "Filesystem commands (mkfs, mount)",
                'networking': "Network commands (nmcli, ip, hostnamectl)",
            }
            hint = category_hints.get(task.category, "Check the task requirements carefully")
            print(f"   {hint}")

        elif hint_level == 2:
            # Hint 2: Base command
            print(fmt.bold("🔧 Base Command:"))
            if expected_commands:
                base_cmd = expected_commands[0].split()[0]
                print(f"   Start with: {fmt.info(base_cmd)}")

        elif hint_level >= 3:
            # Hint 3: Full command structure
            print(fmt.bold("✨ Full Command:"))
            if expected_commands:
                print(f"   {fmt.info(expected_commands[0])}")
            if task.hints:
                print()
                print(fmt.dim("Additional hints:"))
                for hint in task.hints[:2]:
                    print(f"   • {hint}")

        print("━━━━━━━━━━━")
        print()

    def _select_category(self):
        """Select practice category."""
        fmt.clear_screen()
        fmt.print_header("COMMAND RECALL TRAINING - Select Category")

        categories = TaskRegistry.get_all_categories()

        if not categories:
            print(fmt.error("No task categories available"))
            return None

        # Display categories
        for i, cat in enumerate(sorted(categories), 1):
            count = TaskRegistry.get_task_count(cat)
            fmt.print_menu_option(
                i,
                fmt.format_category_name(cat),
                f"{count} tasks available"
            )

        fmt.print_menu_option('Q', "Back to Main Menu")

        # Get selection
        while True:
            choice = input("\nSelect category (number or Q): ").strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    return sorted(categories)[idx]
                else:
                    print(fmt.error("Invalid selection"))
            except ValueError:
                print(fmt.error("Please enter a number or Q"))

    def _select_difficulty(self):
        """Select difficulty level."""
        print()
        print(fmt.bold("Select Difficulty:"))
        fmt.print_menu_option(1, "Easy", "Simpler commands")
        fmt.print_menu_option(2, "Exam", "Exam-level commands (recommended)")
        fmt.print_menu_option(3, "Hard", "Complex commands")

        while True:
            choice = input("\nSelect difficulty [2]: ").strip() or '2'

            if choice == '1':
                return 'easy'
            elif choice == '2':
                return 'exam'
            elif choice == '3':
                return 'hard'
            else:
                print(fmt.error("Invalid selection"))

    def _show_recall_summary(self):
        """Show summary of command recall session."""
        print()
        fmt.print_header("COMMAND RECALL SESSION COMPLETE!")

        print(fmt.bold("📊 Summary:"))
        print(f"   Commands attempted: {self.total_commands}")
        print(f"   Commands correct: {self.correct_commands}")

        accuracy = (self.correct_commands / self.total_commands * 100) if self.total_commands > 0 else 0
        print(f"   Accuracy: {accuracy:.0f}%")
        print()

        # Performance feedback
        if accuracy >= 90:
            print(fmt.success("   🌟 Outstanding! You have excellent command recall!"))
        elif accuracy >= 75:
            print(fmt.success("   👍 Great job! Your command recall is strong!"))
        elif accuracy >= 60:
            print(fmt.info("   📚 Good progress! Keep practicing to improve recall."))
        else:
            print(fmt.warning("   📖 Keep studying! Practice typing commands regularly."))

        print()
        print(fmt.dim("💡 Tip: Regular practice builds muscle memory for exam commands!"))
        print()


def run_command_recall():
    """Run command recall training (convenience function)."""
    session = CommandRecallSession()
    session.start()
