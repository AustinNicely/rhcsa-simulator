"""
Systemd service management tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.command_validators import (
    validate_service_exists, validate_service_state,
    validate_service_enabled, get_service_status
)


logger = logging.getLogger(__name__)


@TaskRegistry.register("services")
class EnableStartServiceTask(BaseTask):
    """Enable and start a systemd service."""

    def __init__(self):
        super().__init__(
            id="service_enable_001",
            category="services",
            difficulty="easy",
            points=5
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service enable/start task."""
        # Common services that might be installed
        services = ['httpd', 'nginx', 'sshd', 'chronyd', 'firewalld']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Configure the '{self.service_name}' service:\n"
            f"  - Start the service\n"
            f"  - Enable the service to start at boot"
        )

        self.hints = [
            "Use 'systemctl start <service>' to start",
            "Use 'systemctl enable <service>' to enable at boot",
            "Verify with 'systemctl status <service>'",
            "Check enabled status with 'systemctl is-enabled <service>'"
        ]

        return self

    def validate(self):
        """Validate service configuration."""
        checks = []
        total_points = 0

        # Check 1: Service is active (3 points)
        if validate_service_state(self.service_name, 'active'):
            checks.append(ValidationCheck(
                name="service_active",
                passed=True,
                points=3,
                message=f"Service '{self.service_name}' is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_active",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service '{self.service_name}' is not running"
            ))

        # Check 2: Service is enabled (2 points)
        if validate_service_enabled(self.service_name, True):
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=True,
                points=2,
                message=f"Service '{self.service_name}' is enabled at boot"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service '{self.service_name}' is not enabled at boot"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class DisableStopServiceTask(BaseTask):
    """Disable and stop a systemd service."""

    def __init__(self):
        super().__init__(
            id="service_disable_001",
            category="services",
            difficulty="easy",
            points=5
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service disable/stop task."""
        services = ['postfix', 'bluetooth', 'cups', 'avahi-daemon']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Configure the '{self.service_name}' service:\n"
            f"  - Stop the service\n"
            f"  - Disable the service from starting at boot"
        )

        self.hints = [
            "Use 'systemctl stop <service>' to stop",
            "Use 'systemctl disable <service>' to prevent boot startup",
            "Verify with 'systemctl status <service>'"
        ]

        return self

    def validate(self):
        """Validate service is stopped and disabled."""
        checks = []
        total_points = 0

        # Check 1: Service is not active (3 points)
        if validate_service_state(self.service_name, 'inactive'):
            checks.append(ValidationCheck(
                name="service_inactive",
                passed=True,
                points=3,
                message=f"Service '{self.service_name}' is stopped"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_inactive",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service '{self.service_name}' is still running"
            ))

        # Check 2: Service is disabled (2 points)
        if validate_service_enabled(self.service_name, False):
            checks.append(ValidationCheck(
                name="service_disabled",
                passed=True,
                points=2,
                message=f"Service '{self.service_name}' is disabled"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_disabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service '{self.service_name}' is still enabled"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class RestartServiceTask(BaseTask):
    """Restart a service and ensure it stays running."""

    def __init__(self):
        super().__init__(
            id="service_restart_001",
            category="services",
            difficulty="exam",
            points=6
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service restart task."""
        services = ['sshd', 'httpd', 'nginx', 'chronyd']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Ensure the '{self.service_name}' service is:\n"
            f"  - Currently running\n"
            f"  - Enabled to start at boot\n"
            f"  - Restart the service to apply any configuration changes"
        )

        self.hints = [
            "Use 'systemctl restart <service>'",
            "Or use 'systemctl reload <service>' if configuration reload is sufficient",
            "Enable with 'systemctl enable <service>'",
            "Verify with 'systemctl status <service>'"
        ]

        return self

    def validate(self):
        """Validate service is running and enabled."""
        checks = []
        total_points = 0

        status = get_service_status(self.service_name)

        # Check 1: Service exists (1 point)
        if status['exists']:
            checks.append(ValidationCheck(
                name="service_exists",
                passed=True,
                points=1,
                message=f"Service '{self.service_name}' exists"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="service_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"Service '{self.service_name}' not found"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Service is active (3 points)
        if status['active']:
            checks.append(ValidationCheck(
                name="service_active",
                passed=True,
                points=3,
                message=f"Service is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_active",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service is not running (state: {status['state']})"
            ))

        # Check 3: Service is enabled (2 points)
        if status['enabled']:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=True,
                points=2,
                message=f"Service is enabled at boot"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service is not enabled at boot"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
