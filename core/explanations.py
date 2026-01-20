"""
Enhanced feedback system with 'why' explanations for RHCSA tasks.
Provides educational context for validation results.
"""

from typing import Dict, Optional


class ExplanationEngine:
    """
    Provides detailed explanations for task validations.
    Explains WHY commands work and what they do under the hood.
    """

    # Command explanations - what each command does and why
    COMMAND_EXPLANATIONS = {
        # User management
        'useradd': {
            'purpose': 'Creates a new user account in /etc/passwd and related files',
            'flags': {
                '-u': 'Sets the numeric UID (user ID) - must be unique',
                '-g': 'Sets the primary group (must exist first)',
                '-G': 'Sets supplementary groups (comma-separated, no spaces)',
                '-m': 'Creates home directory and copies /etc/skel contents',
                '-d': 'Specifies home directory path (use with -m)',
                '-s': 'Sets login shell (must be listed in /etc/shells)',
                '-c': 'Sets GECOS field (comment/full name)',
            },
            'files_modified': ['/etc/passwd', '/etc/shadow', '/etc/group', '/home/*'],
            'common_mistakes': [
                'Forgetting -m flag (home directory not created)',
                'Space after comma in -G groups list',
                'Primary group not existing before user creation',
                'Using -aG instead of -G (only usermod uses -a)',
            ],
        },
        'usermod': {
            'purpose': 'Modifies existing user account properties',
            'flags': {
                '-aG': 'Appends to supplementary groups (without -a, replaces all groups)',
                '-g': 'Changes primary group',
                '-u': 'Changes UID',
                '-s': 'Changes login shell',
                '-L': 'Locks user account',
                '-U': 'Unlocks user account',
            },
            'common_mistakes': [
                'Using -G without -a (removes user from all other groups)',
                'Forgetting that user must log out for group changes to apply',
            ],
        },
        'groupadd': {
            'purpose': 'Creates a new group in /etc/group',
            'flags': {
                '-g': 'Sets the numeric GID (group ID)',
            },
            'files_modified': ['/etc/group', '/etc/gshadow'],
        },

        # SELinux
        'setenforce': {
            'purpose': 'Changes SELinux mode immediately (not persistent)',
            'usage': 'setenforce 0 (Permissive) or setenforce 1 (Enforcing)',
            'important': 'Change is lost on reboot - edit /etc/selinux/config for persistence',
        },
        'semanage fcontext': {
            'purpose': 'Manages SELinux file context mappings in the policy database',
            'flags': {
                '-a': 'Add a new file context mapping',
                '-d': 'Delete an existing mapping',
                '-l': 'List all mappings',
                '-t': 'Specify the SELinux type',
            },
            'pattern': "Path patterns use regex: '/path(/.*)?' matches path and all contents",
            'important': 'Only updates policy database - use restorecon to apply to actual files',
        },
        'restorecon': {
            'purpose': 'Applies SELinux contexts from policy database to actual files',
            'flags': {
                '-R': 'Recursive (apply to directory contents)',
                '-v': 'Verbose (show what changed)',
            },
            'important': 'Must run after semanage fcontext to apply changes',
        },
        'setsebool': {
            'purpose': 'Changes SELinux boolean values',
            'flags': {
                '-P': 'Persistent (survives reboot)',
            },
            'important': 'Without -P, change is lost on reboot',
        },

        # Services
        'systemctl start': {
            'purpose': 'Starts a service immediately',
            'important': 'Does not enable at boot - service stops after reboot',
        },
        'systemctl enable': {
            'purpose': 'Enables service to start at boot (creates symlink)',
            'important': 'Does not start service now - use "enable --now" for both',
        },
        'systemctl enable --now': {
            'purpose': 'Enables AND starts service in one command',
            'important': 'Preferred method - combines enable and start',
        },

        # Permissions
        'chmod': {
            'purpose': 'Changes file permissions (mode bits)',
            'modes': {
                '0755': 'rwxr-xr-x - Owner full, others read/execute',
                '0644': 'rw-r--r-- - Owner read/write, others read only',
                '0440': 'r--r----- - Owner/group read only (sudoers files)',
                '0700': 'rwx------ - Owner only, private directory',
            },
            'special_bits': {
                '4xxx': 'SetUID - runs as file owner',
                '2xxx': 'SetGID - runs as group owner / inherit group',
                '1xxx': 'Sticky bit - only owner can delete',
            },
        },

        # Sudo
        'visudo': {
            'purpose': 'Safely edits sudoers files with syntax checking',
            'important': 'Always use visudo - syntax errors can lock you out',
            'flags': {
                '-f': 'Edit a specific file (e.g., /etc/sudoers.d/username)',
                '-c': 'Check syntax without editing',
            },
        },
    }

    # Check-specific explanations
    CHECK_EXPLANATIONS = {
        'user_exists': {
            'passed': 'User entry found in /etc/passwd',
            'failed': 'User not in /etc/passwd - create with useradd command',
            'how_checked': 'Runs: id <username> or getent passwd <username>',
        },
        'correct_uid': {
            'passed': 'UID matches the required value',
            'failed': 'UID mismatch - use useradd -u <uid> or usermod -u <uid>',
            'how_checked': 'Runs: id -u <username>',
            'why_matters': 'UIDs determine file ownership and NFS compatibility',
        },
        'correct_groups': {
            'passed': 'User belongs to all required groups',
            'failed': 'Missing group membership - use usermod -aG <groups> <user>',
            'how_checked': 'Runs: id <username> or groups <username>',
            'why_matters': 'Group membership controls access to shared resources',
        },
        'home_directory': {
            'passed': 'Home directory exists at expected path',
            'failed': 'Home directory missing - use useradd -m or mkdir + chown',
            'how_checked': 'Checks if directory exists at /home/<username>',
        },
        'service_active': {
            'passed': 'Service is currently running',
            'failed': 'Service not running - use systemctl start <service>',
            'how_checked': 'Runs: systemctl is-active <service>',
        },
        'service_enabled': {
            'passed': 'Service will start automatically at boot',
            'failed': 'Service not enabled - use systemctl enable <service>',
            'how_checked': 'Runs: systemctl is-enabled <service>',
            'why_matters': 'Ensures service survives reboots',
        },
        'current_mode': {
            'passed': 'SELinux is in the required mode',
            'failed': 'SELinux mode incorrect - use setenforce command',
            'how_checked': 'Runs: getenforce',
        },
        'persistent_mode': {
            'passed': 'SELinux config file updated for boot persistence',
            'failed': 'Config not updated - edit /etc/selinux/config SELINUX= line',
            'how_checked': 'Reads: grep ^SELINUX= /etc/selinux/config',
            'why_matters': 'setenforce changes are lost on reboot without this',
        },
        'current_context': {
            'passed': 'File/directory has correct SELinux context type',
            'failed': 'Context mismatch - run restorecon after semanage fcontext',
            'how_checked': 'Runs: ls -Zd <path>',
        },
        'persistent_context': {
            'passed': 'Context mapping saved in SELinux policy database',
            'failed': 'Mapping not saved - use semanage fcontext -a -t <type> <path>',
            'how_checked': 'Runs: semanage fcontext -l | grep <path>',
            'why_matters': 'Without this, context resets on relabel or restorecon',
        },
        'boolean_value': {
            'passed': 'SELinux boolean has the correct value',
            'failed': 'Boolean value wrong - use setsebool <boolean> <value>',
            'how_checked': 'Runs: getsebool <boolean>',
        },
        'persistent_boolean': {
            'passed': 'Boolean change will persist across reboots',
            'failed': 'Boolean not persistent - use setsebool -P flag',
            'how_checked': 'Runs: semanage boolean -l | grep <boolean>',
        },
        'sudo_file_exists': {
            'passed': 'Sudoers drop-in file exists',
            'failed': 'No sudoers file - create /etc/sudoers.d/<username>',
            'how_checked': 'Checks if file exists in /etc/sudoers.d/',
        },
        'sudo_access': {
            'passed': 'User has working sudo privileges',
            'failed': 'Sudo not working - check file syntax/permissions (0440)',
            'how_checked': 'Runs: sudo -l -U <username>',
            'common_issues': [
                'File permissions not 0440',
                'Syntax error in sudoers file',
                'Username typo in file',
            ],
        },
        'directory_exists': {
            'passed': 'Directory exists at the specified path',
            'failed': 'Directory missing - create with mkdir -p',
            'how_checked': 'Checks if path exists and is a directory',
        },
        'group_exists': {
            'passed': 'Group entry found in /etc/group',
            'failed': 'Group missing - create with groupadd command',
            'how_checked': 'Runs: getent group <groupname>',
        },
        'correct_gid': {
            'passed': 'GID matches the required value',
            'failed': 'GID mismatch - use groupadd -g or groupmod -g',
            'how_checked': 'Runs: getent group <groupname> and checks GID field',
        },
    }

    # Task-level explanations
    TASK_EXPLANATIONS = {
        'user_create_001': {
            'objective': 'Understand basic user account creation',
            'real_world': 'Creating user accounts is fundamental sysadmin work',
            'exam_tip': 'Always verify with id command after creating user',
        },
        'user_groups_001': {
            'objective': 'Create users with specific group memberships',
            'real_world': 'Group membership controls access to shared resources',
            'exam_tip': 'Create groups first if they do not exist',
        },
        'sudo_001': {
            'objective': 'Configure passwordless sudo access',
            'real_world': 'Service accounts often need specific sudo privileges',
            'exam_tip': 'Always use visudo -c to check syntax, permissions must be 0440',
        },
        'selinux_mode_001': {
            'objective': 'Change SELinux enforcement mode',
            'real_world': 'Permissive mode useful for troubleshooting, Enforcing for production',
            'exam_tip': 'Remember: setenforce is temporary, config file is permanent',
        },
        'selinux_context_001': {
            'objective': 'Set SELinux file contexts for services',
            'real_world': 'Web servers need httpd_sys_content_t on document roots',
            'exam_tip': 'Two steps: semanage fcontext (save rule) then restorecon (apply)',
        },
        'selinux_boolean_001': {
            'objective': 'Enable SELinux policy features via booleans',
            'real_world': 'Booleans toggle optional policy features without custom policy',
            'exam_tip': 'Use -P flag for persistence, getsebool -a to list all',
        },
        'service_enable_001': {
            'objective': 'Start and enable systemd services',
            'real_world': 'Services must be enabled to survive reboots',
            'exam_tip': 'systemctl enable --now does both in one command',
        },
    }

    @classmethod
    def get_check_explanation(cls, check_name: str, passed: bool) -> Dict:
        """Get explanation for a validation check result."""
        base = cls.CHECK_EXPLANATIONS.get(check_name, {})
        result = {
            'explanation': base.get('passed' if passed else 'failed', 'No explanation available'),
            'how_checked': base.get('how_checked'),
            'why_matters': base.get('why_matters'),
        }
        if not passed and 'common_issues' in base:
            result['common_issues'] = base['common_issues']
        return result

    @classmethod
    def get_command_explanation(cls, command: str) -> Optional[Dict]:
        """Get explanation for a command."""
        # Try exact match first
        if command in cls.COMMAND_EXPLANATIONS:
            return cls.COMMAND_EXPLANATIONS[command]
        # Try base command
        base_cmd = command.split()[0] if ' ' in command else command
        return cls.COMMAND_EXPLANATIONS.get(base_cmd)

    @classmethod
    def get_task_explanation(cls, task_id: str) -> Optional[Dict]:
        """Get explanation for a task."""
        return cls.TASK_EXPLANATIONS.get(task_id)

    @classmethod
    def explain_failure(cls, check_name: str, expected: str, actual: str) -> str:
        """Generate a detailed failure explanation."""
        base = cls.CHECK_EXPLANATIONS.get(check_name, {})
        explanation = base.get('failed', 'Check failed')

        lines = [
            f"Expected: {expected}",
            f"Actual: {actual}",
            f"How to fix: {explanation}",
        ]

        if 'how_checked' in base:
            lines.append(f"Verification: {base['how_checked']}")

        return '\n'.join(lines)


class DiffGenerator:
    """Generates diff views for config file comparisons."""

    @staticmethod
    def generate_config_diff(expected: str, actual: str, filename: str = '') -> str:
        """Generate a simple diff view between expected and actual content."""
        expected_lines = expected.strip().split('\n')
        actual_lines = actual.strip().split('\n')

        output = []
        if filename:
            output.append(f"--- Expected: {filename}")
            output.append(f"+++ Actual: {filename}")
            output.append("")

        # Simple line-by-line comparison
        max_lines = max(len(expected_lines), len(actual_lines))

        for i in range(max_lines):
            exp_line = expected_lines[i] if i < len(expected_lines) else ''
            act_line = actual_lines[i] if i < len(actual_lines) else ''

            if exp_line == act_line:
                output.append(f"  {exp_line}")
            else:
                if exp_line:
                    output.append(f"- {exp_line}")
                if act_line:
                    output.append(f"+ {act_line}")

        return '\n'.join(output)

    @staticmethod
    def generate_selinux_config_expected(mode: str) -> str:
        """Generate expected SELinux config content."""
        return f"""# This file controls the state of SELinux on the system.
SELINUX={mode.lower()}
SELINUXTYPE=targeted"""

    @staticmethod
    def generate_sudoers_expected(username: str, nopasswd: bool = True) -> str:
        """Generate expected sudoers file content."""
        passwd_str = "NOPASSWD: " if nopasswd else ""
        return f"{username} ALL=(ALL) {passwd_str}ALL"


# Convenience functions
def explain_check(check_name: str, passed: bool) -> Dict:
    """Get explanation for a check result."""
    return ExplanationEngine.get_check_explanation(check_name, passed)


def explain_command(command: str) -> Optional[Dict]:
    """Get explanation for a command."""
    return ExplanationEngine.get_command_explanation(command)


def explain_task(task_id: str) -> Optional[Dict]:
    """Get explanation for a task."""
    return ExplanationEngine.get_task_explanation(task_id)
