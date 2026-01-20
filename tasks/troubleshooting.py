"""
Troubleshooting tasks for RHCSA Simulator.
Presents broken systems that users must diagnose and fix.
"""

import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.safe_executor import execute_safe
from validators.command_validators import (
    validate_service_state, validate_service_enabled,
    validate_user_exists, get_user_groups
)
from validators.file_validators import (
    validate_file_exists, validate_file_contains,
    get_file_permissions, get_selinux_type
)


logger = logging.getLogger(__name__)


@dataclass
class TroubleshootingClue:
    """A clue to help diagnose the problem."""
    level: int  # 1 = vague, 2 = helpful, 3 = direct
    text: str
    command: Optional[str] = None  # Command that reveals the clue


@dataclass
class BrokenState:
    """Describes a broken system state."""
    symptom: str
    root_cause: str
    fix_commands: List[str]
    verification: str
    clues: List[TroubleshootingClue] = field(default_factory=list)


class TroubleshootingTask(BaseTask):
    """Base class for troubleshooting tasks."""

    def __init__(self, id: str, category: str, difficulty: str, points: int):
        super().__init__(id=id, category=category, difficulty=difficulty, points=points)
        self.symptom = ""
        self.root_cause = ""
        self.clues: List[TroubleshootingClue] = []
        self.fix_verification: Callable = None

    def get_clue(self, level: int) -> Optional[TroubleshootingClue]:
        """Get a clue at the specified level."""
        for clue in self.clues:
            if clue.level == level:
                return clue
        return None


# ============================================================================
# SERVICE TROUBLESHOOTING
# ============================================================================

@TaskRegistry.register("troubleshooting")
class SSHNotStartingTask(TroubleshootingTask):
    """Troubleshoot SSH service that won't start."""

    def __init__(self):
        super().__init__(
            id="troubleshoot_ssh_001",
            category="troubleshooting",
            difficulty="exam",
            points=12
        )
        self.problem_type = None
        self.problem_details = {}

    def generate(self, **params):
        """Generate SSH troubleshooting scenario."""
        # Different SSH problems
        problems = [
            {
                'type': 'selinux_port',
                'symptom': 'sshd fails to start with "Permission denied" binding to port',
                'description': "The SSH service fails to start. When you check the status, "
                              "you see errors about binding to a port.",
                'clues': [
                    TroubleshootingClue(1, "Check what's preventing the service from starting", "systemctl status sshd"),
                    TroubleshootingClue(2, "SELinux might be blocking non-standard ports", "ausearch -m AVC -ts recent"),
                    TroubleshootingClue(3, "Use semanage to allow SSH on the configured port", "semanage port -l | grep ssh"),
                ],
            },
            {
                'type': 'config_syntax',
                'symptom': 'sshd fails with configuration file error',
                'description': "The SSH service fails to start. The error mentions "
                              "a problem with the configuration file.",
                'clues': [
                    TroubleshootingClue(1, "Check the service status for error details", "systemctl status sshd -l"),
                    TroubleshootingClue(2, "Validate the SSH configuration syntax", "sshd -t"),
                    TroubleshootingClue(3, "Look for typos or invalid options in /etc/ssh/sshd_config"),
                ],
            },
            {
                'type': 'missing_hostkey',
                'symptom': 'sshd fails because host keys are missing',
                'description': "The SSH service fails to start. The error indicates "
                              "missing host keys.",
                'clues': [
                    TroubleshootingClue(1, "Check what files SSH needs", "ls -la /etc/ssh/"),
                    TroubleshootingClue(2, "SSH needs host keys to operate", "ls /etc/ssh/ssh_host_*"),
                    TroubleshootingClue(3, "Regenerate host keys", "ssh-keygen -A"),
                ],
            },
        ]

        problem = random.choice(problems)
        self.problem_type = problem['type']
        self.problem_details = problem

        self.description = (
            f"TROUBLESHOOTING: SSH Service Won't Start\n"
            f"{'=' * 50}\n\n"
            f"Symptom: {problem['symptom']}\n\n"
            f"{problem['description']}\n\n"
            f"Your task:\n"
            f"  1. Diagnose the root cause\n"
            f"  2. Fix the problem\n"
            f"  3. Ensure SSH service starts successfully\n"
            f"  4. Ensure SSH is enabled at boot"
        )

        self.hints = [
            "Start by checking systemctl status sshd",
            "Look at journal logs: journalctl -xeu sshd",
            "Check for SELinux denials: ausearch -m AVC -ts recent",
        ]

        self.clues = problem['clues']

        return self

    def validate(self):
        """Validate that SSH is fixed and running."""
        checks = []
        total_points = 0

        # Check 1: Service is active (6 points)
        if validate_service_state('sshd', 'active'):
            checks.append(ValidationCheck(
                name="sshd_running",
                passed=True,
                points=6,
                message="SSHD service is running"
            ))
            total_points += 6
        else:
            checks.append(ValidationCheck(
                name="sshd_running",
                passed=False,
                points=0,
                max_points=6,
                message="SSHD service is not running"
            ))

        # Check 2: Service is enabled (3 points)
        if validate_service_enabled('sshd', True):
            checks.append(ValidationCheck(
                name="sshd_enabled",
                passed=True,
                points=3,
                message="SSHD is enabled at boot"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="sshd_enabled",
                passed=False,
                points=0,
                max_points=3,
                message="SSHD is not enabled at boot"
            ))

        # Check 3: Can actually connect (3 points)
        result = execute_safe(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=3',
                              'localhost', 'exit'], timeout=5)
        # We expect this to fail with permission denied (no key), but not connection refused
        if result.returncode != 255:  # 255 is connection refused
            checks.append(ValidationCheck(
                name="sshd_accepting",
                passed=True,
                points=3,
                message="SSHD is accepting connections"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="sshd_accepting",
                passed=False,
                points=0,
                max_points=3,
                message="SSHD is not accepting connections"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("troubleshooting")
class WebServerNotWorkingTask(TroubleshootingTask):
    """Troubleshoot Apache web server issues."""

    def __init__(self):
        super().__init__(
            id="troubleshoot_httpd_001",
            category="troubleshooting",
            difficulty="exam",
            points=15
        )
        self.problem_type = None

    def generate(self, **params):
        """Generate web server troubleshooting scenario."""
        problems = [
            {
                'type': 'selinux_content',
                'symptom': 'Apache returns 403 Forbidden for all pages',
                'description': "Apache is running but all pages return 403 Forbidden errors. "
                              "The files exist and have correct Unix permissions.",
            },
            {
                'type': 'selinux_port',
                'symptom': 'Apache fails to start on custom port',
                'description': "Apache is configured to use port 8080 but fails to start. "
                              "SELinux is in enforcing mode.",
            },
            {
                'type': 'document_root_perms',
                'symptom': 'Apache cannot read document root',
                'description': "Apache starts but returns 403 errors. The document root "
                              "directory has incorrect ownership or permissions.",
            },
            {
                'type': 'firewall_blocking',
                'symptom': 'Cannot access web server from network',
                'description': "Apache is running and works locally (curl localhost), "
                              "but cannot be accessed from other machines.",
            },
        ]

        problem = random.choice(problems)
        self.problem_type = problem['type']

        self.description = (
            f"TROUBLESHOOTING: Web Server Not Working\n"
            f"{'=' * 50}\n\n"
            f"Symptom: {problem['symptom']}\n\n"
            f"{problem['description']}\n\n"
            f"Your task:\n"
            f"  1. Diagnose why the web server isn't working\n"
            f"  2. Fix the underlying issue\n"
            f"  3. Verify the web server serves content correctly"
        )

        self.hints = [
            "Check Apache status: systemctl status httpd",
            "Look for SELinux denials: ausearch -m AVC -ts recent",
            "Check document root permissions: ls -laZ /var/www/html",
            "Test locally: curl -I http://localhost",
            "Check firewall: firewall-cmd --list-all",
        ]

        return self

    def validate(self):
        """Validate web server is working."""
        checks = []
        total_points = 0

        # Check 1: Service running (4 points)
        if validate_service_state('httpd', 'active'):
            checks.append(ValidationCheck(
                name="httpd_running",
                passed=True,
                points=4,
                message="Apache is running"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="httpd_running",
                passed=False,
                points=0,
                max_points=4,
                message="Apache is not running"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Service enabled (2 points)
        if validate_service_enabled('httpd', True):
            checks.append(ValidationCheck(
                name="httpd_enabled",
                passed=True,
                points=2,
                message="Apache is enabled at boot"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="httpd_enabled",
                passed=False,
                points=0,
                max_points=2,
                message="Apache is not enabled at boot"
            ))

        # Check 3: Can access content (5 points)
        result = execute_safe(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                              'http://localhost/'], timeout=10)
        if result.success and result.stdout.strip() == '200':
            checks.append(ValidationCheck(
                name="httpd_serving",
                passed=True,
                points=5,
                message="Apache is serving content (HTTP 200)"
            ))
            total_points += 5
        else:
            http_code = result.stdout.strip() if result.success else 'N/A'
            checks.append(ValidationCheck(
                name="httpd_serving",
                passed=False,
                points=0,
                max_points=5,
                message=f"Apache not serving content correctly (HTTP {http_code})"
            ))

        # Check 4: SELinux context correct (4 points)
        doc_root = '/var/www/html'
        context = get_selinux_type(doc_root)
        if context and 'httpd' in context:
            checks.append(ValidationCheck(
                name="selinux_context",
                passed=True,
                points=4,
                message="Document root has correct SELinux context"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="selinux_context",
                passed=False,
                points=0,
                max_points=4,
                message=f"Document root SELinux context incorrect: {context}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("troubleshooting")
class UserCannotLoginTask(TroubleshootingTask):
    """Troubleshoot user login issues."""

    def __init__(self):
        super().__init__(
            id="troubleshoot_login_001",
            category="troubleshooting",
            difficulty="exam",
            points=10
        )
        self.username = None
        self.problem_type = None

    def generate(self, **params):
        """Generate user login troubleshooting scenario."""
        self.username = params.get('username', f'loginuser{random.randint(1, 99)}')

        problems = [
            {
                'type': 'locked_account',
                'symptom': f'User {self.username} cannot log in - account locked',
                'description': f"The user '{self.username}' reports they cannot log in. "
                              f"Their password is correct but login fails.",
            },
            {
                'type': 'expired_password',
                'symptom': f'User {self.username} password has expired',
                'description': f"The user '{self.username}' cannot log in because their "
                              f"password has expired and needs to be reset.",
            },
            {
                'type': 'invalid_shell',
                'symptom': f'User {self.username} has invalid login shell',
                'description': f"The user '{self.username}' authenticates but gets "
                              f"immediately disconnected. Their shell might be invalid.",
            },
            {
                'type': 'no_home_dir',
                'symptom': f'User {self.username} has no home directory',
                'description': f"The user '{self.username}' can authenticate but sees "
                              f"errors about their home directory not existing.",
            },
        ]

        problem = random.choice(problems)
        self.problem_type = problem['type']

        self.description = (
            f"TROUBLESHOOTING: User Cannot Log In\n"
            f"{'=' * 50}\n\n"
            f"Symptom: {problem['symptom']}\n\n"
            f"{problem['description']}\n\n"
            f"Your task:\n"
            f"  1. Diagnose why the user cannot log in\n"
            f"  2. Fix the issue\n"
            f"  3. Verify the user can log in successfully"
        )

        self.hints = [
            f"Check user status: passwd -S {self.username}",
            f"Check password aging: chage -l {self.username}",
            f"Check user's shell: getent passwd {self.username}",
            f"Check if home exists: ls -la /home/{self.username}",
            "Check /var/log/secure for authentication failures",
        ]

        return self

    def validate(self):
        """Validate user can log in."""
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

        # Check 2: Account not locked (3 points)
        result = execute_safe(['passwd', '-S', self.username])
        if result.success and ' P ' in result.stdout:  # P = usable password
            checks.append(ValidationCheck(
                name="account_unlocked",
                passed=True,
                points=3,
                message="Account is not locked"
            ))
            total_points += 3
        else:
            status = result.stdout.split()[1] if result.success else 'unknown'
            checks.append(ValidationCheck(
                name="account_unlocked",
                passed=False,
                points=0,
                max_points=3,
                message=f"Account may be locked (status: {status})"
            ))

        # Check 3: Valid shell (2 points)
        result = execute_safe(['getent', 'passwd', self.username])
        if result.success:
            shell = result.stdout.strip().split(':')[-1]
            valid_shells_result = execute_safe(['cat', '/etc/shells'])
            valid_shells = valid_shells_result.stdout if valid_shells_result.success else ''

            if shell in valid_shells or shell == '/bin/bash':
                checks.append(ValidationCheck(
                    name="valid_shell",
                    passed=True,
                    points=2,
                    message=f"User has valid shell: {shell}"
                ))
                total_points += 2
            else:
                checks.append(ValidationCheck(
                    name="valid_shell",
                    passed=False,
                    points=0,
                    max_points=2,
                    message=f"User has invalid shell: {shell}"
                ))

        # Check 4: Home directory exists (3 points)
        home_dir = f"/home/{self.username}"
        if validate_file_exists(home_dir, file_type='directory'):
            checks.append(ValidationCheck(
                name="home_exists",
                passed=True,
                points=3,
                message=f"Home directory exists: {home_dir}"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="home_exists",
                passed=False,
                points=0,
                max_points=3,
                message=f"Home directory missing: {home_dir}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("troubleshooting")
class FilesystemNotMountingTask(TroubleshootingTask):
    """Troubleshoot filesystem mount issues."""

    def __init__(self):
        super().__init__(
            id="troubleshoot_mount_001",
            category="troubleshooting",
            difficulty="hard",
            points=12
        )
        self.mountpoint = None
        self.problem_type = None

    def generate(self, **params):
        """Generate filesystem mount troubleshooting scenario."""
        self.mountpoint = params.get('mountpoint', '/mnt/data')

        problems = [
            {
                'type': 'bad_fstab',
                'symptom': 'System fails to boot due to fstab error',
                'description': "After adding an entry to /etc/fstab, the system fails "
                              "to boot normally. You need to fix the fstab entry.",
            },
            {
                'type': 'wrong_uuid',
                'symptom': 'Filesystem not mounting - UUID not found',
                'description': "A filesystem that was mounting correctly before no longer "
                              "mounts. The UUID in fstab might be incorrect.",
            },
            {
                'type': 'missing_mountpoint',
                'symptom': 'Mount fails - directory does not exist',
                'description': "The mount command fails because the mount point "
                              "directory does not exist.",
            },
            {
                'type': 'fsck_needed',
                'symptom': 'Filesystem needs repair before mounting',
                'description': "The filesystem cannot be mounted and the system suggests "
                              "running filesystem repair tools.",
            },
        ]

        problem = random.choice(problems)
        self.problem_type = problem['type']

        self.description = (
            f"TROUBLESHOOTING: Filesystem Not Mounting\n"
            f"{'=' * 50}\n\n"
            f"Symptom: {problem['symptom']}\n\n"
            f"{problem['description']}\n\n"
            f"Mount point: {self.mountpoint}\n\n"
            f"Your task:\n"
            f"  1. Identify why the filesystem won't mount\n"
            f"  2. Fix the issue\n"
            f"  3. Verify the filesystem mounts correctly\n"
            f"  4. Ensure it will mount on next boot"
        )

        self.hints = [
            "Check current mounts: mount | grep /mnt",
            "Test fstab: mount -a",
            "Check fstab syntax: cat /etc/fstab",
            "Get device UUID: blkid",
            "Create mountpoint if missing: mkdir -p /mnt/data",
        ]

        return self

    def validate(self):
        """Validate filesystem is mounted correctly."""
        checks = []
        total_points = 0

        # Check 1: Mountpoint exists (2 points)
        if validate_file_exists(self.mountpoint, file_type='directory'):
            checks.append(ValidationCheck(
                name="mountpoint_exists",
                passed=True,
                points=2,
                message=f"Mount point exists: {self.mountpoint}"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="mountpoint_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Mount point missing: {self.mountpoint}"
            ))

        # Check 2: Filesystem is mounted (5 points)
        result = execute_safe(['findmnt', self.mountpoint])
        if result.success:
            checks.append(ValidationCheck(
                name="filesystem_mounted",
                passed=True,
                points=5,
                message=f"Filesystem is mounted at {self.mountpoint}"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="filesystem_mounted",
                passed=False,
                points=0,
                max_points=5,
                message=f"Filesystem not mounted at {self.mountpoint}"
            ))

        # Check 3: Entry in fstab (5 points)
        if validate_file_contains('/etc/fstab', self.mountpoint):
            # Also verify fstab is valid
            test_result = execute_safe(['findmnt', '--verify', '--fstab'])
            if test_result.returncode == 0 or 'success' in test_result.stdout.lower():
                checks.append(ValidationCheck(
                    name="fstab_entry",
                    passed=True,
                    points=5,
                    message="Valid fstab entry exists for mount point"
                ))
                total_points += 5
            else:
                checks.append(ValidationCheck(
                    name="fstab_entry",
                    passed=False,
                    points=2,  # Partial credit
                    max_points=5,
                    message="fstab entry exists but may have issues"
                ))
                total_points += 2
        else:
            checks.append(ValidationCheck(
                name="fstab_entry",
                passed=False,
                points=0,
                max_points=5,
                message="No fstab entry for mount point (won't persist)"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("troubleshooting")
class SudoNotWorkingTask(TroubleshootingTask):
    """Troubleshoot sudo access issues."""

    def __init__(self):
        super().__init__(
            id="troubleshoot_sudo_001",
            category="troubleshooting",
            difficulty="exam",
            points=10
        )
        self.username = None
        self.problem_type = None

    def generate(self, **params):
        """Generate sudo troubleshooting scenario."""
        self.username = params.get('username', f'sudouser{random.randint(1, 99)}')

        problems = [
            {
                'type': 'syntax_error',
                'symptom': f'sudo fails with syntax error for {self.username}',
                'description': f"User '{self.username}' was given sudo access but when "
                              f"they try to use sudo, they get a syntax error.",
            },
            {
                'type': 'wrong_permissions',
                'symptom': 'sudoers.d file is being ignored',
                'description': f"A sudoers file was created for '{self.username}' but "
                              f"sudo doesn't recognize their privileges. The file "
                              f"might have wrong permissions.",
            },
            {
                'type': 'not_in_wheel',
                'symptom': f'{self.username} not in sudoers',
                'description': f"User '{self.username}' was supposed to get sudo access "
                              f"via the wheel group but it's not working.",
            },
        ]

        problem = random.choice(problems)
        self.problem_type = problem['type']

        self.description = (
            f"TROUBLESHOOTING: Sudo Not Working\n"
            f"{'=' * 50}\n\n"
            f"Symptom: {problem['symptom']}\n\n"
            f"{problem['description']}\n\n"
            f"Your task:\n"
            f"  1. Diagnose why sudo isn't working\n"
            f"  2. Fix the configuration\n"
            f"  3. Verify the user has sudo access"
        )

        self.hints = [
            f"Test sudo: sudo -l -U {self.username}",
            "Check sudoers syntax: visudo -c",
            "Check file permissions: ls -l /etc/sudoers.d/",
            f"Check group membership: groups {self.username}",
            "Sudoers.d files must be 0440 or root-owned",
        ]

        return self

    def validate(self):
        """Validate sudo is working."""
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

        # Check 2: Sudoers syntax valid (3 points)
        result = execute_safe(['visudo', '-c'])
        if result.success:
            checks.append(ValidationCheck(
                name="sudoers_syntax",
                passed=True,
                points=3,
                message="Sudoers files have valid syntax"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="sudoers_syntax",
                passed=False,
                points=0,
                max_points=3,
                message="Sudoers syntax error detected"
            ))

        # Check 3: User has sudo access (5 points)
        result = execute_safe(['sudo', '-l', '-U', self.username])
        if result.success and 'not allowed' not in result.stdout.lower():
            checks.append(ValidationCheck(
                name="sudo_access",
                passed=True,
                points=5,
                message=f"User '{self.username}' has sudo privileges"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="sudo_access",
                passed=False,
                points=0,
                max_points=5,
                message=f"User '{self.username}' does not have sudo access"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
