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


@TaskRegistry.register("permissions")
class SharedDirectoryTask(BaseTask):
    """Configure a shared directory with SGID and sticky bit."""

    def __init__(self):
        super().__init__(
            id="perm_shared_dir_001",
            category="permissions",
            difficulty="exam",
            points=12
        )
        self.dir_path = None
        self.group = None

    def generate(self, **params):
        """Generate shared directory task."""
        dir_suffix = random.randint(1, 99)
        self.dir_path = params.get('dir', f'/shared/project{dir_suffix}')
        self.group = params.get('group', random.choice(['developers', 'team', 'shared']))

        self.description = (
            f"Configure a collaborative shared directory at '{self.dir_path}':\n"
            f"  - Create the directory (including parent directories)\n"
            f"  - Set group ownership to: {self.group}\n"
            f"  - All new files/directories should inherit the group '{self.group}'\n"
            f"  - Users should only be able to delete their own files\n"
            f"  - Group members should have full read/write/execute access\n"
            f"  - Others should have no access"
        )

        self.hints = [
            f"Create directory: mkdir -p {self.dir_path}",
            f"Set ownership: chown :{self.group} {self.dir_path}",
            "SGID makes new files inherit group: chmod g+s or 2xxx",
            "Sticky bit prevents deletion by others: chmod +t or 1xxx",
            "Combined: chmod 3770 (SGID + Sticky + rwxrwx---)",
            "Verify: ls -ld should show drwxrws--T or drwxrwx--t"
        ]

        return self

    def validate(self):
        """Validate shared directory configuration."""
        checks = []
        total_points = 0

        # Check 1: Directory exists (2 points)
        if validate_file_exists(self.dir_path, file_type='directory'):
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=True,
                points=2,
                message=f"Directory exists: {self.dir_path}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Directory not found: {self.dir_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Correct group ownership (3 points)
        actual_group = get_file_group(self.dir_path)
        if actual_group == self.group:
            checks.append(ValidationCheck(
                name="group_ownership",
                passed=True,
                points=3,
                message=f"Group ownership correct: {self.group}"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="group_ownership",
                passed=False,
                points=0,
                max_points=3,
                message=f"Group mismatch: expected {self.group}, got {actual_group}"
            ))

        # Check 3: SGID bit set (3 points)
        actual_perms = get_file_permissions(self.dir_path)
        sgid_set = actual_perms and len(actual_perms) == 4 and actual_perms[0] in ['2', '3', '6', '7']
        if sgid_set:
            checks.append(ValidationCheck(
                name="sgid_set",
                passed=True,
                points=3,
                message=f"SGID bit is set (new files inherit group)"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="sgid_set",
                passed=False,
                points=0,
                max_points=3,
                message=f"SGID bit not set (permissions: {actual_perms})"
            ))

        # Check 4: Sticky bit set (2 points)
        sticky_set = actual_perms and len(actual_perms) == 4 and actual_perms[0] in ['1', '3', '5', '7']
        if sticky_set:
            checks.append(ValidationCheck(
                name="sticky_set",
                passed=True,
                points=2,
                message=f"Sticky bit is set (users can only delete own files)"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="sticky_set",
                passed=False,
                points=0,
                max_points=2,
                message=f"Sticky bit not set (permissions: {actual_perms})"
            ))

        # Check 5: Group has rwx, others have no access (2 points)
        if actual_perms and len(actual_perms) >= 3:
            base_perms = actual_perms[-3:]  # Get last 3 digits
            group_ok = base_perms[1] == '7'  # Group has rwx
            others_ok = base_perms[2] == '0'  # Others have nothing

            if group_ok and others_ok:
                checks.append(ValidationCheck(
                    name="base_perms",
                    passed=True,
                    points=2,
                    message=f"Base permissions correct (group rwx, others none)"
                ))
                total_points += 2
            elif group_ok:
                checks.append(ValidationCheck(
                    name="base_perms",
                    passed=True,
                    points=1,
                    message=f"Group has full access (partial: others should have none)"
                ))
                total_points += 1
            else:
                checks.append(ValidationCheck(
                    name="base_perms",
                    passed=False,
                    points=0,
                    max_points=2,
                    message=f"Permissions incorrect: {actual_perms}"
                ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("permissions")
class DefaultACLTask(BaseTask):
    """Set default ACL on a directory for inheritance."""

    def __init__(self):
        super().__init__(
            id="acl_default_001",
            category="permissions",
            difficulty="exam",
            points=10
        )
        self.dir_path = None
        self.acl_user = None
        self.acl_perms = None

    def generate(self, **params):
        """Generate default ACL task."""
        dir_suffix = random.randint(1, 99)
        self.dir_path = params.get('dir', f'/data/acltest{dir_suffix}')
        self.acl_user = params.get('user', random.choice(['webadmin', 'developer', 'operator']))
        self.acl_perms = params.get('perms', random.choice(['rwx', 'rw-', 'r-x']))

        self.description = (
            f"Configure default ACL on directory '{self.dir_path}':\n"
            f"  - Create the directory if it doesn't exist\n"
            f"  - Set a DEFAULT ACL for user '{self.acl_user}' with permissions: {self.acl_perms}\n"
            f"  - All NEW files and directories created inside should automatically\n"
            f"    grant these permissions to '{self.acl_user}'\n"
            f"  - This is for inheritance, not just the directory itself"
        )

        self.hints = [
            f"Create directory: mkdir -p {self.dir_path}",
            f"Set DEFAULT ACL: setfacl -d -m u:{self.acl_user}:{self.acl_perms} {self.dir_path}",
            "The -d flag sets DEFAULT ACL (affects new files)",
            "Without -d, ACL only affects the directory itself",
            "Verify with: getfacl {dir} | grep default"
        ]

        return self

    def validate(self):
        """Validate default ACL configuration."""
        checks = []
        total_points = 0

        # Check 1: Directory exists (2 points)
        if validate_file_exists(self.dir_path, file_type='directory'):
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=True,
                points=2,
                message=f"Directory exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Directory not found: {self.dir_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Default ACL is set (8 points)
        try:
            import subprocess
            result = subprocess.run(
                ['getfacl', self.dir_path],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout

            # Look for default ACL entry
            expected_patterns = [
                f"default:user:{self.acl_user}:{self.acl_perms}",
                f"default:user:{self.acl_user}:{self.acl_perms.replace('-', '')}"
            ]

            default_acl_found = any(pattern in output for pattern in expected_patterns)

            if default_acl_found:
                checks.append(ValidationCheck(
                    name="default_acl",
                    passed=True,
                    points=8,
                    message=f"Default ACL set correctly for user:{self.acl_user}:{self.acl_perms}"
                ))
                total_points += 8
            elif f"default:user:{self.acl_user}" in output:
                # User has default ACL but different permissions
                checks.append(ValidationCheck(
                    name="default_acl",
                    passed=True,
                    points=5,
                    message=f"Default ACL exists for {self.acl_user} but permissions differ"
                ))
                total_points += 5
            elif "default:" in output:
                # Some default ACL exists
                checks.append(ValidationCheck(
                    name="default_acl",
                    passed=True,
                    points=3,
                    message=f"Default ACL exists but not for user {self.acl_user}"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="default_acl",
                    passed=False,
                    points=0,
                    max_points=8,
                    message=f"No default ACL found (use setfacl -d -m ...)"
                ))

        except Exception as e:
            checks.append(ValidationCheck(
                name="default_acl",
                passed=False,
                points=0,
                max_points=8,
                message=f"Could not verify ACL: {e}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("permissions")
class RecursivePermissionsTask(BaseTask):
    """Set permissions recursively on a directory tree."""

    def __init__(self):
        super().__init__(
            id="perm_recursive_001",
            category="permissions",
            difficulty="medium",
            points=8
        )
        self.dir_path = None
        self.dir_perms = None
        self.file_perms = None
        self.owner = None
        self.group = None

    def generate(self, **params):
        """Generate recursive permissions task."""
        dir_suffix = random.randint(1, 99)
        self.dir_path = params.get('dir', f'/var/data/project{dir_suffix}')
        self.owner = params.get('owner', random.choice(['root', 'admin']))
        self.group = params.get('group', random.choice(['webteam', 'developers']))
        self.dir_perms = params.get('dir_perms', '755')
        self.file_perms = params.get('file_perms', '644')

        self.description = (
            f"Set permissions recursively on '{self.dir_path}':\n"
            f"  - Owner: {self.owner}\n"
            f"  - Group: {self.group}\n"
            f"  - Directory permissions: {self.dir_perms}\n"
            f"  - File permissions: {self.file_perms}\n"
            f"  - Apply to ALL files and subdirectories"
        )

        self.hints = [
            f"Change ownership recursively: chown -R {self.owner}:{self.group} {self.dir_path}",
            f"Set directory permissions: find {self.dir_path} -type d -exec chmod {self.dir_perms} {{}} \\;",
            f"Set file permissions: find {self.dir_path} -type f -exec chmod {self.file_perms} {{}} \\;",
            "Alternative: chmod -R sets same perms for all (less precise)",
            "Use find to distinguish files vs directories"
        ]

        return self

    def validate(self):
        """Validate recursive permissions."""
        checks = []
        total_points = 0

        # Check 1: Directory exists (2 points)
        if validate_file_exists(self.dir_path, file_type='directory'):
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=True,
                points=2,
                message=f"Directory exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="dir_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Directory not found: {self.dir_path}"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Ownership is correct (3 points)
        actual_owner = get_file_owner(self.dir_path)
        actual_group = get_file_group(self.dir_path)

        if actual_owner == self.owner and actual_group == self.group:
            checks.append(ValidationCheck(
                name="ownership",
                passed=True,
                points=3,
                message=f"Ownership correct: {self.owner}:{self.group}"
            ))
            total_points += 3
        elif actual_owner == self.owner or actual_group == self.group:
            checks.append(ValidationCheck(
                name="ownership",
                passed=True,
                points=1,
                message=f"Partial ownership match: {actual_owner}:{actual_group}"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="ownership",
                passed=False,
                points=0,
                max_points=3,
                message=f"Ownership incorrect: {actual_owner}:{actual_group}"
            ))

        # Check 3: Directory has correct permissions (3 points)
        if validate_file_permissions(self.dir_path, self.dir_perms):
            checks.append(ValidationCheck(
                name="dir_permissions",
                passed=True,
                points=3,
                message=f"Directory permissions correct: {self.dir_perms}"
            ))
            total_points += 3
        else:
            actual_perms = get_file_permissions(self.dir_path)
            checks.append(ValidationCheck(
                name="dir_permissions",
                passed=False,
                points=0,
                max_points=3,
                message=f"Directory permissions: expected {self.dir_perms}, got {actual_perms}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
