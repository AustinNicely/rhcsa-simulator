"""
File permissions and ACL tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.file_validators import (
    validate_file_exists, validate_file_permissions,
    validate_file_ownership, validate_acl_entry,
    get_file_permissions, get_file_owner, get_file_group
)


logger = logging.getLogger(__name__)


@TaskRegistry.register("permissions")
class SetFilePermissionsTask(BaseTask):
    """Set standard permissions on a file."""

    def __init__(self):
        super().__init__(
            id="perm_basic_001",
            category="permissions",
            difficulty="easy",
            points=4
        )
        self.file_path = None
        self.permissions = None

    def generate(self, **params):
        """Generate permissions task."""
        file_suffix = random.randint(1, 99)
        self.file_path = params.get('file', f'/tmp/testfile{file_suffix}.txt')
        perm_choices = ['644', '640', '600', '755', '750', '700']
        self.permissions = params.get('perms', random.choice(perm_choices))

        self.description = (
            f"Set permissions on file '{self.file_path}':\n"
            f"  - Permissions: {self.permissions} (octal)"
        )

        self.hints = [
            "Use 'chmod' command",
            f"Format: chmod {self.permissions} {self.file_path}",
            "Verify with 'ls -l' or 'stat' command"
        ]

        return self

    def validate(self):
        """Validate file permissions."""
        checks = []
        total_points = 0

        # Check 1: File exists (1 point)
        if validate_file_exists(self.file_path):
            checks.append(ValidationCheck(
                name="file_exists",
                passed=True,
                points=1,
                message=f"File exists: {self.file_path}"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="file_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"File not found: {self.file_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct permissions (3 points)
        if validate_file_permissions(self.file_path, self.permissions):
            checks.append(ValidationCheck(
                name="permissions",
                passed=True,
                points=3,
                message=f"Permissions correct: {self.permissions}"
            ))
            total_points += 3
        else:
            actual = get_file_permissions(self.file_path)
            checks.append(ValidationCheck(
                name="permissions",
                passed=False,
                points=0,
                max_points=3,
                message=f"Permissions incorrect: expected {self.permissions}, got {actual}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("permissions")
class SetFileOwnershipTask(BaseTask):
    """Set file ownership (owner and group)."""

    def __init__(self):
        super().__init__(
            id="perm_owner_001",
            category="permissions",
            difficulty="easy",
            points=5
        )
        self.file_path = None
        self.owner = None
        self.group = None

    def generate(self, **params):
        """Generate ownership task."""
        file_suffix = random.randint(1, 99)
        self.file_path = params.get('file', f'/tmp/ownertest{file_suffix}.txt')
        self.owner = params.get('owner', random.choice(['root', 'nobody', 'apache']))
        self.group = params.get('group', random.choice(['root', 'wheel', 'apache']))

        self.description = (
            f"Set ownership on file '{self.file_path}':\n"
            f"  - Owner: {self.owner}\n"
            f"  - Group: {self.group}"
        )

        self.hints = [
            "Use 'chown' command",
            f"Format: chown {self.owner}:{self.group} {self.file_path}",
            "Or use chown for owner and chgrp for group separately",
            "Verify with 'ls -l' command"
        ]

        return self

    def validate(self):
        """Validate file ownership."""
        checks = []
        total_points = 0

        # Check 1: File exists (1 point)
        if validate_file_exists(self.file_path):
            checks.append(ValidationCheck(
                name="file_exists",
                passed=True,
                points=1,
                message=f"File exists"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="file_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"File not found: {self.file_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct owner (2 points)
        actual_owner = get_file_owner(self.file_path)
        if actual_owner == self.owner:
            checks.append(ValidationCheck(
                name="correct_owner",
                passed=True,
                points=2,
                message=f"Owner correct: {self.owner}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_owner",
                passed=False,
                points=0,
                max_points=2,
                message=f"Owner incorrect: expected {self.owner}, got {actual_owner}"
            ))

        # Check 3: Correct group (2 points)
        actual_group = get_file_group(self.file_path)
        if actual_group == self.group:
            checks.append(ValidationCheck(
                name="correct_group",
                passed=True,
                points=2,
                message=f"Group correct: {self.group}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="correct_group",
                passed=False,
                points=0,
                max_points=2,
                message=f"Group incorrect: expected {self.group}, got {actual_group}"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("permissions")
class SetACLTask(BaseTask):
    """Set ACL on a file."""

    def __init__(self):
        super().__init__(
            id="acl_001",
            category="permissions",
            difficulty="exam",
            points=8
        )
        self.file_path = None
        self.acl_user = None
        self.acl_perms = None

    def generate(self, **params):
        """Generate ACL task."""
        file_suffix = random.randint(1, 99)
        self.file_path = params.get('file', f'/tmp/acltest{file_suffix}.txt')
        self.acl_user = params.get('user', random.choice(['apache', 'nginx', 'nobody']))
        self.acl_perms = params.get('perms', random.choice(['r--', 'rw-', 'r-x']))

        self.description = (
            f"Configure ACL on file '{self.file_path}':\n"
            f"  - Grant user '{self.acl_user}' permissions: {self.acl_perms}\n"
            f"  - Use ACLs (Access Control Lists)"
        )

        self.hints = [
            "Use 'setfacl' command",
            f"Format: setfacl -m u:{self.acl_user}:{self.acl_perms} {self.file_path}",
            "Verify with 'getfacl <file>'",
            "Note: ACL permissions format is read(r), write(w), execute(x)"
        ]

        return self

    def validate(self):
        """Validate ACL configuration."""
        checks = []
        total_points = 0

        # Check 1: File exists (2 points)
        if validate_file_exists(self.file_path):
            checks.append(ValidationCheck(
                name="file_exists",
                passed=True,
                points=2,
                message=f"File exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="file_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"File not found: {self.file_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: ACL entry exists (6 points)
        if validate_acl_entry(self.file_path, 'user', self.acl_user, self.acl_perms):
            checks.append(ValidationCheck(
                name="acl_entry",
                passed=True,
                points=6,
                message=f"ACL configured correctly: user:{self.acl_user}:{self.acl_perms}"
            ))
            total_points += 6
        else:
            checks.append(ValidationCheck(
                name="acl_entry",
                passed=False,
                points=0,
                max_points=6,
                message=f"ACL not configured correctly for user {self.acl_user}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("permissions")
class SetSpecialPermissionsTask(BaseTask):
    """Set special permissions (setuid, setgid, sticky bit)."""

    def __init__(self):
        super().__init__(
            id="perm_special_001",
            category="permissions",
            difficulty="exam",
            points=7
        )
        self.file_path = None
        self.special_bit = None
        self.permissions = None

    def generate(self, **params):
        """Generate special permissions task."""
        file_suffix = random.randint(1, 99)
        self.file_path = params.get('file', f'/tmp/specialperm{file_suffix}')

        special_options = [
            ('setuid', '4755', 'Set the setuid bit (4)'),
            ('setgid', '2755', 'Set the setgid bit (2)'),
            ('sticky', '1777', 'Set the sticky bit (1)')
        ]

        self.special_bit, self.permissions, description = random.choice(special_options)

        self.description = (
            f"Set special permissions on '{self.file_path}':\n"
            f"  - {description}\n"
            f"  - Final permissions: {self.permissions}"
        )

        self.hints = [
            f"Use 'chmod {self.permissions} <file>'",
            "Special bits: setuid=4, setgid=2, sticky=1",
            "Combine with standard permissions",
            "Verify with 'ls -l' (shows as 's' or 't' in permissions)"
        ]

        return self

    def validate(self):
        """Validate special permissions."""
        checks = []
        total_points = 0

        # Check 1: File exists (2 points)
        if validate_file_exists(self.file_path):
            checks.append(ValidationCheck(
                name="file_exists",
                passed=True,
                points=2,
                message=f"File exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="file_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"File not found: {self.file_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct permissions including special bit (5 points)
        if validate_file_permissions(self.file_path, self.permissions):
            checks.append(ValidationCheck(
                name="special_permissions",
                passed=True,
                points=5,
                message=f"Special permissions correct: {self.permissions}"
            ))
            total_points += 5
        else:
            actual = get_file_permissions(self.file_path)
            checks.append(ValidationCheck(
                name="special_permissions",
                passed=False,
                points=0,
                max_points=5,
                message=f"Permissions incorrect: expected {self.permissions}, got {actual}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
