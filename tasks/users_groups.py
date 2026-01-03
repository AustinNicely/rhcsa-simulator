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
                message=f"Shell mismatch: expected {self.shell}, got {actual_shell}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
