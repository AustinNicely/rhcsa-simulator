"""
User and group management tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.command_validators import (
    validate_user_exists, get_user_uid, get_user_gid,
    get_user_groups, get_user_shell, get_user_home,
    validate_group_exists, get_group_gid, check_sudo_access
)
from validators.file_validators import validate_file_exists, validate_file_contains


logger = logging.getLogger(__name__)


@TaskRegistry.register("users_groups")
class CreateUserTask(BaseTask):
    """Create a user with specific UID."""

    def __init__(self):
        super().__init__(
            id="user_create_001",
            category="users_groups",
            difficulty="easy",
            points=5
        )
        self.username = None
        self.uid = None

    def generate(self, **params):
        """Generate random user creation task."""
        self.username = params.get('username', f'testuser{random.randint(1, 99)}')
        self.uid = params.get('uid', random.randint(2000, 2999))

        self.description = (
            f"Create a user named '{self.username}' with the following specifications:\n"
            f"  - UID: {self.uid}\n"
            f"  - Home directory: /home/{self.username}\n"
            f"  - Login shell: /bin/bash"
        )

        self.hints = [
            "Use the 'useradd' command",
            "Check 'useradd --help' for UID and home directory options",
            "Verify with 'id <username>' command"
        ]

        return self

    def validate(self):
        """Validate user creation."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct UID (2 points)
        actual_uid = get_user_uid(self.username)
        if actual_uid == str(self.uid):
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=True,
                points=2,
                message=f"UID is correct: {self.uid}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=False,
                points=0,
                max_points=2,
                message=f"UID mismatch: expected {self.uid}, got {actual_uid}"
            ))

        # Check 3: Home directory exists (1 point)
        home_dir = f"/home/{self.username}"
        if validate_file_exists(home_dir, file_type='directory'):
            checks.append(ValidationCheck(
                name="home_directory",
                passed=True,
                points=1,
                message=f"Home directory exists: {home_dir}"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="home_directory",
                passed=False,
                points=0,
                max_points=1,
                message=f"Home directory missing: {home_dir}"
            ))

        passed = total_points >= (self.points * 0.6)  # 60% to pass
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class CreateUserWithGroupsTask(BaseTask):
    """Create user with specific groups."""

    def __init__(self):
        super().__init__(
            id="user_groups_001",
            category="users_groups",
            difficulty="exam",
            points=8
        )
        self.username = None
        self.uid = None
        self.primary_group = None
        self.supplementary_groups = None

    def generate(self, **params):
        """Generate user with groups task."""
        self.username = f'examuser{random.randint(1, 99)}'
        self.uid = random.randint(2000, 2999)
        self.primary_group = random.choice(["users", "wheel"])
        self.supplementary_groups = ["developers", "sysadmin"]

        self.description = (
            f"Create a user named '{self.username}' with the following requirements:\n"
            f"  - UID: {self.uid}\n"
            f"  - Primary group: {self.primary_group}\n"
            f"  - Supplementary groups: {', '.join(self.supplementary_groups)}\n"
            f"  - Home directory: /home/{self.username}\n"
            f"  - Login shell: /bin/bash"
        )

        self.hints = [
            "Use 'useradd' with -g (primary group) and -G (supplementary groups)",
            "You may need to create groups first with 'groupadd'",
            "Verify with 'id <username>' or 'groups <username>'"
        ]

        return self

    def validate(self):
        """Validate user with groups."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct UID (2 points)
        actual_uid = get_user_uid(self.username)
        if actual_uid == str(self.uid):
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=True,
                points=2,
                message=f"UID is correct: {self.uid}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=False,
                points=0,
                max_points=2,
                message=f"UID mismatch: expected {self.uid}, got {actual_uid}"
            ))

        # Check 3: Correct groups (4 points)
        actual_groups = get_user_groups(self.username)
        expected_groups = set([self.primary_group] + self.supplementary_groups)

        if expected_groups.issubset(set(actual_groups)):
            checks.append(ValidationCheck(
                name="correct_groups",
                passed=True,
                points=4,
                message=f"All required groups present: {', '.join(expected_groups)}"
            ))
            total_points += 4
        else:
            missing = expected_groups - set(actual_groups)
            checks.append(ValidationCheck(
                name="correct_groups",
                passed=False,
                points=0,
                max_points=4,
                message=f"Missing groups: {', '.join(missing)}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class ConfigureSudoTask(BaseTask):
    """Configure sudo access for user."""

    def __init__(self):
        super().__init__(
            id="sudo_001",
            category="users_groups",
            difficulty="exam",
            points=6
        )
        self.username = None

    def generate(self, **params):
        """Generate sudo configuration task."""
        self.username = params.get('username', f'sysadmin{random.randint(1, 99)}')

        self.description = (
            f"Configure sudo access for user '{self.username}':\n"
            f"  - Allow user to run ALL commands with sudo\n"
            f"  - No password required (NOPASSWD)\n"
            f"  - Add configuration to /etc/sudoers.d/ directory\n"
            f"  - Ensure proper file permissions (0440)"
        )

        self.hints = [
            "Create a file in /etc/sudoers.d/ directory",
            "Format: username ALL=(ALL) NOPASSWD: ALL",
            "Set permissions to 0440 or use 'visudo'",
            "Test with 'sudo -l -U <username>'"
        ]

        return self

    def validate(self):
        """Validate sudo configuration."""
        checks = []
        total_points = 0

        # Check 1: User exists (1 point)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=1,
                message=f"User '{self.username}' exists"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Sudo file exists (2 points)
        sudo_file = f"/etc/sudoers.d/{self.username}"
        if validate_file_exists(sudo_file):
            checks.append(ValidationCheck(
                name="sudo_file_exists",
                passed=True,
                points=2,
                message=f"Sudo configuration file exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="sudo_file_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Sudo configuration file not found in /etc/sudoers.d/"
            ))

        # Check 3: Sudo access granted (3 points)
        if check_sudo_access(self.username):
            checks.append(ValidationCheck(
                name="sudo_access",
                passed=True,
                points=3,
                message=f"Sudo access configured correctly"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="sudo_access",
                passed=False,
                points=0,
                max_points=3,
                message=f"Sudo access not working"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class CreateGroupTask(BaseTask):
    """Create a group with specific GID."""

    def __init__(self):
        super().__init__(
            id="group_create_001",
            category="users_groups",
            difficulty="easy",
            points=4
        )
        self.groupname = None
        self.gid = None

    def generate(self, **params):
        """Generate group creation task."""
        self.groupname = params.get('groupname', f'testgroup{random.randint(1, 99)}')
        self.gid = params.get('gid', random.randint(3000, 3999))

        self.description = (
            f"Create a group named '{self.groupname}' with GID {self.gid}"
        )

        self.hints = [
            "Use the 'groupadd' command",
            "Use the -g option to specify GID",
            "Verify with 'getent group <groupname>'"
        ]

        return self

    def validate(self):
        """Validate group creation."""
        checks = []
        total_points = 0

        # Check 1: Group exists (2 points)
        if validate_group_exists(self.groupname):
            checks.append(ValidationCheck(
                name="group_exists",
                passed=True,
                points=2,
                message=f"Group '{self.groupname}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="group_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Group '{self.groupname}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct GID (2 points)
        actual_gid = get_group_gid(self.groupname)
        if actual_gid == str(self.gid):
            checks.append(ValidationCheck(
                name="correct_gid",
                passed=True,
                points=2,
                message=f"GID is correct: {self.gid}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_gid",
                passed=False,
                points=0,
                max_points=2,
                message=f"GID mismatch: expected {self.gid}, got {actual_gid}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class ModifyUserShellTask(BaseTask):
    """Change user's login shell."""

    def __init__(self):
        super().__init__(
            id="user_shell_001",
            category="users_groups",
            difficulty="easy",
            points=4
        )
        self.username = None
        self.shell = None

    def generate(self, **params):
        """Generate shell modification task."""
        self.username = params.get('username', f'shelluser{random.randint(1, 99)}')
        self.shell = params.get('shell', random.choice(['/bin/sh', '/bin/bash', '/usr/bin/zsh']))

        self.description = (
            f"Change the login shell for user '{self.username}' to: {self.shell}"
        )

        self.hints = [
            "Use the 'usermod' command with -s option",
            "Or use the 'chsh' command",
            "Verify with 'getent passwd <username>'"
        ]

        return self

    def validate(self):
        """Validate shell modification."""
        checks = []
        total_points = 0

        # Check 1: User exists (1 point)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=1,
                message=f"User '{self.username}' exists"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct shell (3 points)
        actual_shell = get_user_shell(self.username)
        if actual_shell == self.shell:
            checks.append(ValidationCheck(
                name="correct_shell",
                passed=True,
                points=3,
                message=f"Login shell is correct: {self.shell}"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="correct_shell",
                passed=False,
                points=0,
                max_points=3,
                message=f"Shell mismatch: expected {self.shell}, got {actual_shell}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class PasswordAgingTask(BaseTask):
    """Configure password aging policies for a user."""

    def __init__(self):
        super().__init__(
            id="password_aging_001",
            category="users_groups",
            difficulty="exam",
            points=10
        )
        self.username = None
        self.max_days = None
        self.min_days = None
        self.warn_days = None
        self.force_change = False

    def generate(self, **params):
        """Generate password aging task."""
        self.username = params.get('username', f'ageuser{random.randint(1, 99)}')
        self.max_days = params.get('max_days', random.choice([30, 60, 90, 180]))
        self.min_days = params.get('min_days', random.choice([0, 1, 7]))
        self.warn_days = params.get('warn_days', random.choice([7, 14]))
        self.force_change = params.get('force_change', random.choice([True, False]))

        force_text = "\n  - User must change password on next login" if self.force_change else ""

        self.description = (
            f"Configure password aging for user '{self.username}':\n"
            f"  - Maximum days between password changes: {self.max_days}\n"
            f"  - Minimum days between password changes: {self.min_days}\n"
            f"  - Warning days before expiration: {self.warn_days}"
            f"{force_text}"
        )

        self.hints = [
            "Use the 'chage' command to set password aging policies",
            f"chage -M {self.max_days} -m {self.min_days} -W {self.warn_days} {self.username}",
            "To force password change on next login: chage -d 0 username",
            "Verify with: chage -l username"
        ]

        return self

    def validate(self):
        """Validate password aging configuration."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check password aging values from /etc/shadow
        try:
            import subprocess
            result = subprocess.run(
                ['chage', '-l', self.username],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout

            # Check 2: Maximum days (3 points)
            if f"Maximum number of days between password change" in output:
                if str(self.max_days) in output.split("Maximum number of days between password change")[1].split('\n')[0]:
                    checks.append(ValidationCheck(
                        name="max_days",
                        passed=True,
                        points=3,
                        message=f"Maximum days set correctly: {self.max_days}"
                    ))
                    total_points += 3
                else:
                    checks.append(ValidationCheck(
                        name="max_days",
                        passed=False,
                        points=0,
                        max_points=3,
                        message=f"Maximum days not set to {self.max_days}"
                    ))

            # Check 3: Minimum days (2 points)
            if f"Minimum number of days between password change" in output:
                if str(self.min_days) in output.split("Minimum number of days between password change")[1].split('\n')[0]:
                    checks.append(ValidationCheck(
                        name="min_days",
                        passed=True,
                        points=2,
                        message=f"Minimum days set correctly: {self.min_days}"
                    ))
                    total_points += 2
                else:
                    checks.append(ValidationCheck(
                        name="min_days",
                        passed=False,
                        points=0,
                        max_points=2,
                        message=f"Minimum days not set to {self.min_days}"
                    ))

            # Check 4: Warning days (2 points)
            if "Number of days of warning before password expires" in output:
                if str(self.warn_days) in output.split("Number of days of warning before password expires")[1].split('\n')[0]:
                    checks.append(ValidationCheck(
                        name="warn_days",
                        passed=True,
                        points=2,
                        message=f"Warning days set correctly: {self.warn_days}"
                    ))
                    total_points += 2
                else:
                    checks.append(ValidationCheck(
                        name="warn_days",
                        passed=False,
                        points=0,
                        max_points=2,
                        message=f"Warning days not set to {self.warn_days}"
                    ))

            # Check 5: Force change on next login (1 point, only if required)
            if self.force_change:
                if "password must be changed" in output.lower() or "Last password change" in output and "password must be changed" in output:
                    checks.append(ValidationCheck(
                        name="force_change",
                        passed=True,
                        points=1,
                        message="Password change required on next login"
                    ))
                    total_points += 1
                else:
                    checks.append(ValidationCheck(
                        name="force_change",
                        passed=False,
                        points=0,
                        max_points=1,
                        message="Password change on next login not configured"
                    ))

        except Exception as e:
            checks.append(ValidationCheck(
                name="chage_check",
                passed=False,
                points=0,
                max_points=8,
                message=f"Could not verify password aging: {e}"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class LockUnlockUserTask(BaseTask):
    """Lock or unlock a user account."""

    def __init__(self):
        super().__init__(
            id="user_lock_001",
            category="users_groups",
            difficulty="easy",
            points=5
        )
        self.username = None
        self.action = None  # 'lock' or 'unlock'

    def generate(self, **params):
        """Generate lock/unlock user task."""
        self.username = params.get('username', f'lockuser{random.randint(1, 99)}')
        self.action = params.get('action', random.choice(['lock', 'unlock']))

        if self.action == 'lock':
            self.description = (
                f"Lock the user account '{self.username}':\n"
                f"  - Prevent the user from logging in\n"
                f"  - Do NOT delete the account\n"
                f"  - The account should be locked but still exist"
            )
        else:
            self.description = (
                f"Unlock the user account '{self.username}':\n"
                f"  - Allow the user to log in again\n"
                f"  - The account should be fully accessible"
            )

        self.hints = [
            f"Use 'usermod -L username' to lock an account",
            f"Use 'usermod -U username' to unlock an account",
            "Alternative: 'passwd -l username' to lock, 'passwd -u username' to unlock",
            "Verify with: passwd -S username (shows LK for locked, PS for password set)"
        ]

        return self

    def validate(self):
        """Validate user lock/unlock."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Account lock status (3 points)
        try:
            import subprocess
            result = subprocess.run(
                ['passwd', '-S', self.username],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout.strip()

            # passwd -S output: username LK/PS/NP ... (LK=locked, PS=password set, NP=no password)
            is_locked = ' LK ' in output or ' L ' in output

            if self.action == 'lock':
                if is_locked:
                    checks.append(ValidationCheck(
                        name="account_locked",
                        passed=True,
                        points=3,
                        message=f"Account is correctly locked"
                    ))
                    total_points += 3
                else:
                    checks.append(ValidationCheck(
                        name="account_locked",
                        passed=False,
                        points=0,
                        max_points=3,
                        message=f"Account is NOT locked (expected locked)"
                    ))
            else:  # unlock
                if not is_locked:
                    checks.append(ValidationCheck(
                        name="account_unlocked",
                        passed=True,
                        points=3,
                        message=f"Account is correctly unlocked"
                    ))
                    total_points += 3
                else:
                    checks.append(ValidationCheck(
                        name="account_unlocked",
                        passed=False,
                        points=0,
                        max_points=3,
                        message=f"Account is still locked (expected unlocked)"
                    ))

        except Exception as e:
            checks.append(ValidationCheck(
                name="lock_status",
                passed=False,
                points=0,
                max_points=3,
                message=f"Could not verify lock status: {e}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class CreateNologinUserTask(BaseTask):
    """Create a system/service user that cannot log in interactively."""

    def __init__(self):
        super().__init__(
            id="user_nologin_001",
            category="users_groups",
            difficulty="medium",
            points=6
        )
        self.username = None
        self.uid = None

    def generate(self, **params):
        """Generate nologin user task."""
        self.username = params.get('username', f'svcaccount{random.randint(1, 99)}')
        self.uid = params.get('uid', random.randint(2000, 2999))

        self.description = (
            f"Create a service account named '{self.username}':\n"
            f"  - UID: {self.uid}\n"
            f"  - The user should NOT be able to log in interactively\n"
            f"  - This is typically used for running services/daemons"
        )

        self.hints = [
            "Use -s /sbin/nologin or -s /bin/false for the shell",
            f"Example: useradd -u {self.uid} -s /sbin/nologin {self.username}",
            "/sbin/nologin shows a polite message, /bin/false just exits",
            "Verify with: getent passwd username | grep nologin"
        ]

        return self

    def validate(self):
        """Validate nologin user creation."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct UID (2 points)
        actual_uid = get_user_uid(self.username)
        if actual_uid == str(self.uid):
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=True,
                points=2,
                message=f"UID is correct: {self.uid}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_uid",
                passed=False,
                points=0,
                max_points=2,
                message=f"UID mismatch: expected {self.uid}, got {actual_uid}"
            ))

        # Check 3: Shell is nologin or false (2 points)
        actual_shell = get_user_shell(self.username)
        nologin_shells = ['/sbin/nologin', '/usr/sbin/nologin', '/bin/false']
        if actual_shell in nologin_shells:
            checks.append(ValidationCheck(
                name="nologin_shell",
                passed=True,
                points=2,
                message=f"Shell correctly set to prevent login: {actual_shell}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="nologin_shell",
                passed=False,
                points=0,
                max_points=2,
                message=f"Shell allows login: {actual_shell} (expected nologin or false)"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("users_groups")
class UserExpirationTask(BaseTask):
    """Set account expiration date for a user."""

    def __init__(self):
        super().__init__(
            id="user_expire_001",
            category="users_groups",
            difficulty="medium",
            points=6
        )
        self.username = None
        self.expire_date = None

    def generate(self, **params):
        """Generate user expiration task."""
        self.username = params.get('username', f'tempuser{random.randint(1, 99)}')

        # Generate a future date
        import datetime
        days_ahead = random.choice([30, 60, 90, 180, 365])
        future_date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        self.expire_date = params.get('expire_date', future_date.strftime('%Y-%m-%d'))

        self.description = (
            f"Configure account expiration for user '{self.username}':\n"
            f"  - Account should expire on: {self.expire_date}\n"
            f"  - After this date, the user will NOT be able to log in\n"
            f"  - This is useful for contractor/temporary accounts"
        )

        self.hints = [
            f"Use 'chage -E {self.expire_date} {self.username}'",
            f"Or use 'usermod -e {self.expire_date} {self.username}'",
            "Date format is YYYY-MM-DD",
            "Verify with: chage -l username | grep 'Account expires'"
        ]

        return self

    def validate(self):
        """Validate user expiration."""
        checks = []
        total_points = 0

        # Check 1: User exists (2 points)
        if validate_user_exists(self.username):
            checks.append(ValidationCheck(
                name="user_exists",
                passed=True,
                points=2,
                message=f"User '{self.username}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="user_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"User '{self.username}' does not exist"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Expiration date set (4 points)
        try:
            import subprocess
            result = subprocess.run(
                ['chage', '-l', self.username],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout

            # Parse expected date to various formats
            import datetime
            exp_date = datetime.datetime.strptime(self.expire_date, '%Y-%m-%d')
            date_formats = [
                exp_date.strftime('%b %d, %Y'),  # Jan 15, 2025
                exp_date.strftime('%B %d, %Y'),  # January 15, 2025
                self.expire_date,  # 2025-01-15
            ]

            if "Account expires" in output:
                expire_line = output.split("Account expires")[1].split('\n')[0]
                date_found = any(fmt in expire_line for fmt in date_formats)

                if date_found:
                    checks.append(ValidationCheck(
                        name="expire_date",
                        passed=True,
                        points=4,
                        message=f"Account expiration set correctly: {self.expire_date}"
                    ))
                    total_points += 4
                elif "never" not in expire_line.lower():
                    # Date is set but might be in different format
                    checks.append(ValidationCheck(
                        name="expire_date",
                        passed=True,
                        points=3,
                        message=f"Account expiration is set (partial credit)"
                    ))
                    total_points += 3
                else:
                    checks.append(ValidationCheck(
                        name="expire_date",
                        passed=False,
                        points=0,
                        max_points=4,
                        message=f"Account expiration not set (shows 'never')"
                    ))
            else:
                checks.append(ValidationCheck(
                    name="expire_date",
                    passed=False,
                    points=0,
                    max_points=4,
                    message=f"Could not find account expiration info"
                ))

        except Exception as e:
            checks.append(ValidationCheck(
                name="expire_check",
                passed=False,
                points=0,
                max_points=4,
                message=f"Could not verify expiration: {e}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
