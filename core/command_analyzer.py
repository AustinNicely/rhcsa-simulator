"""
Command History Analyzer for AI Feedback.
Tracks and analyzes user commands during practice sessions.
"""

import os
import subprocess
import logging
from datetime import datetime
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


class CommandHistoryAnalyzer:
    """Analyzes bash command history during practice sessions."""

    def __init__(self):
        """Initialize command history analyzer."""
        self.session_start_time = None
        self.commands_during_session = []
        self.baseline_history_size = 0

    def start_session(self):
        """Mark the start of a practice session."""
        self.session_start_time = datetime.now()
        self.baseline_history_size = self._get_history_size()
        self.commands_during_session = []
        logger.info(f"Started command tracking session at {self.session_start_time}")

    def get_session_commands(self) -> List[Dict]:
        """
        Get commands executed during this session.

        Returns:
            List[Dict]: Commands with timestamp, command text, and metadata
        """
        if self.session_start_time is None:
            return []

        try:
            # Read bash history
            history_commands = self._read_bash_history()

            # Filter to session commands (after baseline)
            session_commands = history_commands[self.baseline_history_size:]

            # Parse and structure commands
            structured_commands = []
            for i, cmd in enumerate(session_commands, 1):
                structured_commands.append({
                    'sequence': i,
                    'command': cmd.strip(),
                    'category': self._categorize_command(cmd),
                    'is_destructive': self._is_destructive(cmd),
                    'is_query': self._is_query_command(cmd)
                })

            self.commands_during_session = structured_commands
            return structured_commands

        except Exception as e:
            logger.error(f"Error getting session commands: {e}")
            return []

    def _read_bash_history(self) -> List[str]:
        """
        Read bash history from multiple sources.

        Returns:
            List[str]: List of command strings
        """
        commands = []

        # Try history command first
        try:
            result = subprocess.run(
                ['bash', '-c', 'history'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    # Format: "  123  command here"
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 2:
                        commands.append(parts[1])
        except Exception as e:
            logger.debug(f"Could not read from history command: {e}")

        # Fallback: Read .bash_history file
        if not commands:
            try:
                history_file = os.path.expanduser('~/.bash_history')
                if os.path.exists(history_file):
                    with open(history_file, 'r', errors='ignore') as f:
                        commands = [line.strip() for line in f if line.strip()]
            except Exception as e:
                logger.debug(f"Could not read .bash_history: {e}")

        return commands

    def _get_history_size(self) -> int:
        """Get current size of bash history."""
        try:
            commands = self._read_bash_history()
            return len(commands)
        except:
            return 0

    def _categorize_command(self, cmd: str) -> str:
        """
        Categorize a command by its primary function.

        Args:
            cmd: Command string

        Returns:
            str: Category name
        """
        cmd_lower = cmd.lower().strip()

        # Get the first word (actual command)
        first_word = cmd_lower.split()[0] if cmd_lower else ""

        # User management
        if first_word in ['useradd', 'usermod', 'userdel', 'groupadd', 'groupmod', 'passwd']:
            return 'user_management'

        # Permissions
        if first_word in ['chmod', 'chown', 'chgrp', 'setfacl', 'getfacl']:
            return 'permissions'

        # SELinux
        if first_word in ['semanage', 'restorecon', 'chcon', 'setsebool', 'getsebool']:
            return 'selinux'

        # Services
        if first_word in ['systemctl', 'service']:
            return 'services'

        # Boot/GRUB
        if first_word in ['grub2-mkconfig', 'grub-mkconfig', 'hostnamectl']:
            return 'boot'

        # LVM
        if first_word in ['pvcreate', 'vgcreate', 'lvcreate', 'pvs', 'vgs', 'lvs', 'lvextend', 'pvdisplay', 'vgdisplay', 'lvdisplay']:
            return 'lvm'

        # Filesystems
        if first_word in ['mkfs', 'mount', 'umount', 'mkswap', 'swapon', 'swapoff', 'blkid', 'lsblk']:
            return 'filesystem'

        # Networking
        if first_word in ['nmcli', 'ip', 'ifconfig', 'route']:
            return 'networking'

        # Processes
        if first_word in ['kill', 'killall', 'pkill', 'nice', 'renice', 'ps', 'top', 'pgrep']:
            return 'processes'

        # Scheduling
        if first_word in ['crontab', 'at', 'atq', 'atrm']:
            return 'scheduling'

        # Containers
        if first_word in ['podman', 'docker']:
            return 'containers'

        # Essential tools
        if first_word in ['find', 'grep', 'tar', 'gzip', 'bzip2', 'xz']:
            return 'essential_tools'

        # Verification
        if first_word in ['cat', 'ls', 'grep', 'less', 'more', 'head', 'tail']:
            return 'verification'

        # Editing
        if first_word in ['vi', 'vim', 'nano', 'emacs', 'sed', 'awk']:
            return 'editing'

        return 'other'

    def _is_destructive(self, cmd: str) -> bool:
        """
        Check if command is potentially destructive.

        Args:
            cmd: Command string

        Returns:
            bool: True if destructive
        """
        destructive_commands = [
            'rm ', 'rmdir', 'userdel', 'groupdel', 'lvremove', 'vgremove', 'pvremove',
            'umount', 'kill ', 'killall', 'pkill', 'dd ', 'mkfs', 'fdisk', 'parted'
        ]

        cmd_lower = cmd.lower()
        return any(dest in cmd_lower for dest in destructive_commands)

    def _is_query_command(self, cmd: str) -> bool:
        """
        Check if command is a query/read-only command.

        Args:
            cmd: Command string

        Returns:
            bool: True if query command
        """
        query_commands = [
            'ls', 'cat', 'grep', 'less', 'more', 'head', 'tail', 'ps', 'top',
            'df', 'du', 'free', 'lsblk', 'blkid', 'pvs', 'vgs', 'lvs',
            'systemctl status', 'systemctl is-', 'id ', 'groups', 'getent',
            'getenforce', 'getsebool', 'mount | grep'
        ]

        cmd_lower = cmd.lower()
        return any(query in cmd_lower for query in query_commands)

    def analyze_approach(self, task_description: str, expected_commands: List[str]) -> Dict:
        """
        Analyze user's approach compared to expected solution.

        Args:
            task_description: Description of the task
            expected_commands: List of expected command patterns

        Returns:
            Dict: Analysis results
        """
        session_commands = self.get_session_commands()

        analysis = {
            'total_commands': len(session_commands),
            'categories_used': list(set(cmd['category'] for cmd in session_commands)),
            'destructive_commands': [cmd for cmd in session_commands if cmd['is_destructive']],
            'query_commands': [cmd for cmd in session_commands if cmd['is_query']],
            'unexpected_commands': [],
            'missing_steps': [],
            'efficiency_score': 0
        }

        # Calculate efficiency (fewer commands = higher score, but penalize if too few)
        if len(session_commands) > 0:
            optimal_count = len(expected_commands)
            actual_count = len([cmd for cmd in session_commands if not cmd['is_query']])

            if actual_count == optimal_count:
                analysis['efficiency_score'] = 100
            elif actual_count < optimal_count:
                analysis['efficiency_score'] = max(0, 50 - (optimal_count - actual_count) * 10)
            else:
                # More commands than optimal, but still ok
                analysis['efficiency_score'] = max(0, 100 - (actual_count - optimal_count) * 5)

        return analysis

    def get_command_sequence(self) -> str:
        """
        Get formatted command sequence for display.

        Returns:
            str: Formatted command list
        """
        commands = self.get_session_commands()

        if not commands:
            return "No commands recorded in this session."

        lines = []
        lines.append("Commands executed during this task:")
        lines.append("=" * 60)

        for cmd in commands:
            category_tag = f"[{cmd['category']}]"
            lines.append(f"  {cmd['sequence']}. {cmd['command']} {category_tag}")

        return "\n".join(lines)
