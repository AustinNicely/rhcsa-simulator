"""
Container management tasks for RHCSA exam (Podman).
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.system_validators import (
    validate_container_running, validate_container_exists,
    validate_image_exists
)
from validators.safe_executor import execute_safe
from validators.file_validators import validate_file_contains


logger = logging.getLogger(__name__)


@TaskRegistry.register("containers")
class PullContainerImageTask(BaseTask):
    """Pull a container image using podman."""

    def __init__(self):
        super().__init__(
            id="container_pull_001",
            category="containers",
            difficulty="easy",
            points=6
        )
        self.image_name = None

    def generate(self, **params):
        """Generate image pull task."""
        images = [
            'registry.access.redhat.com/ubi8/ubi:latest',
            'docker.io/library/httpd:latest',
            'docker.io/library/nginx:latest',
            'registry.access.redhat.com/ubi9/ubi-minimal:latest',
        ]

        self.image_name = params.get('image', random.choice(images))

        self.description = (
            f"Pull a container image:\n"
            f"  - Image: {self.image_name}\n"
            f"  - Use podman to pull the image\n"
            f"  - Verify the image is available locally"
        )

        self.hints = [
            f"Pull image: podman pull {self.image_name}",
            "List images: podman images",
            "Search for images: podman search <name>",
            "Inspect image: podman inspect {image}"
        ]

        return self

    def validate(self):
        """Validate image is pulled."""
        checks = []
        total_points = 0

        # Check if image exists locally
        if validate_image_exists(self.image_name):
            checks.append(ValidationCheck(
                name="image_pulled",
                passed=True,
                points=6,
                message=f"Image '{self.image_name}' is available locally"
            ))
            total_points += 6
        else:
            # Try with short name
            short_name = self.image_name.split('/')[-1]
            if validate_image_exists(short_name):
                checks.append(ValidationCheck(
                    name="image_pulled",
                    passed=True,
                    points=6,
                    message=f"Image is available locally"
                ))
                total_points += 6
            else:
                checks.append(ValidationCheck(
                    name="image_pulled",
                    passed=False,
                    points=0,
                    max_points=6,
                    message=f"Image '{self.image_name}' not found locally"
                ))

        passed = total_points >= (self.points * 0.8)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("containers")
class RunContainerTask(BaseTask):
    """Run a container with specific options."""

    def __init__(self):
        super().__init__(
            id="container_run_001",
            category="containers",
            difficulty="medium",
            points=10
        )
        self.container_name = None
        self.image_name = None
        self.port_mapping = None

    def generate(self, **params):
        """Generate container run task."""
        self.container_name = params.get('name', f'webapp{random.randint(1,99)}')
        self.image_name = params.get('image', 'httpd:latest')
        self.port_mapping = params.get('port', f'{random.randint(8080,8090)}:80')

        host_port, container_port = self.port_mapping.split(':')

        self.description = (
            f"Run a container:\n"
            f"  - Container name: {self.container_name}\n"
            f"  - Image: {self.image_name}\n"
            f"  - Port mapping: Host {host_port} -> Container {container_port}\n"
            f"  - Run in detached mode (background)\n"
            f"  - Container must be running"
        )

        self.hints = [
            f"Run container: podman run -d --name {self.container_name} -p {self.port_mapping} {self.image_name}",
            "-d runs in detached (background) mode",
            "-p maps ports: host_port:container_port",
            "Check status: podman ps",
            f"View logs: podman logs {self.container_name}"
        ]

        return self

    def validate(self):
        """Validate container is running."""
        checks = []
        total_points = 0

        # Check 1: Container exists (4 points)
        if validate_container_exists(self.container_name):
            checks.append(ValidationCheck(
                name="container_exists",
                passed=True,
                points=4,
                message=f"Container '{self.container_name}' exists"
            ))
            total_points += 4

            # Check 2: Container is running (6 points)
            if validate_container_running(self.container_name):
                checks.append(ValidationCheck(
                    name="container_running",
                    passed=True,
                    points=6,
                    message=f"Container is running"
                ))
                total_points += 6
            else:
                checks.append(ValidationCheck(
                    name="container_running",
                    passed=False,
                    points=0,
                    max_points=6,
                    message=f"Container exists but is not running"
                ))
        else:
            checks.append(ValidationCheck(
                name="container_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Container '{self.container_name}' not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("containers")
class PersistentContainerTask(BaseTask):
    """Configure a container to start automatically via systemd."""

    def __init__(self):
        super().__init__(
            id="container_systemd_001",
            category="containers",
            difficulty="exam",
            points=15
        )
        self.container_name = None
        self.image_name = None
        self.service_name = None

    def generate(self, **params):
        """Generate persistent container task."""
        self.container_name = params.get('name', f'persistent-app{random.randint(1,99)}')
        self.image_name = params.get('image', 'httpd:latest')
        self.service_name = f'container-{self.container_name}.service'

        self.description = (
            f"Configure a persistent container:\n"
            f"  - Container name: {self.container_name}\n"
            f"  - Image: {self.image_name}\n"
            f"  - Container must start automatically at boot\n"
            f"  - Use systemd to manage the container\n"
            f"  - Generate systemd unit file\n"
            f"  - Enable and start the service"
        )

        self.hints = [
            f"Create and run container first: podman run -d --name {self.container_name} {self.image_name}",
            f"Generate systemd unit: podman generate systemd --new --name {self.container_name} > ~/.config/systemd/user/{self.service_name}",
            "Or for system: podman generate systemd --new --name {name} | sudo tee /etc/systemd/system/{service}",
            "Reload systemd: systemctl --user daemon-reload (or sudo systemctl daemon-reload for system)",
            f"Enable: systemctl --user enable {self.service_name}",
            f"Start: systemctl --user start {self.service_name}",
            "For system service, use sudo and omit --user"
        ]

        return self

    def validate(self):
        """Validate container systemd integration."""
        checks = []
        total_points = 0

        # Check 1: Container exists (5 points)
        if validate_container_exists(self.container_name):
            checks.append(ValidationCheck(
                name="container_exists",
                passed=True,
                points=5,
                message=f"Container exists"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="container_exists",
                passed=False,
                points=0,
                max_points=5,
                message=f"Container '{self.container_name}' not found"
            ))

        # Check 2: Container is running (5 points)
        if validate_container_running(self.container_name):
            checks.append(ValidationCheck(
                name="container_running",
                passed=True,
                points=5,
                message=f"Container is running"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="container_running",
                passed=False,
                points=0,
                max_points=5,
                message=f"Container is not running"
            ))

        # Check 3: Systemd service exists and is enabled (5 points)
        # Check both user and system services
        import os
        user_service_path = os.path.expanduser(f'~/.config/systemd/user/{self.service_name}')
        system_service_path = f'/etc/systemd/system/{self.service_name}'

        service_exists = os.path.exists(user_service_path) or os.path.exists(system_service_path)

        if service_exists:
            checks.append(ValidationCheck(
                name="systemd_service",
                passed=True,
                points=5,
                message=f"Systemd service file exists"
            ))
            total_points += 5
        else:
            # Also check for alternative naming patterns
            result = execute_safe(['systemctl', 'list-unit-files', '--no-pager'])
            if result.success and self.container_name in result.stdout:
                checks.append(ValidationCheck(
                    name="systemd_service",
                    passed=True,
                    points=3,
                    message=f"Systemd service exists (partial credit)"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="systemd_service",
                    passed=False,
                    points=0,
                    max_points=5,
                    message=f"Systemd service file not found"
                ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("containers")
class ContainerVolumeTask(BaseTask):
    """Run a container with a volume mount."""

    def __init__(self):
        super().__init__(
            id="container_volume_001",
            category="containers",
            difficulty="medium",
            points=12
        )
        self.container_name = None
        self.image_name = None
        self.host_path = None
        self.container_path = None

    def generate(self, **params):
        """Generate container volume task."""
        self.container_name = params.get('name', f'data-container{random.randint(1,99)}')
        self.image_name = params.get('image', 'ubi8/ubi:latest')
        self.host_path = params.get('host_path', '/opt/containerdata')
        self.container_path = params.get('container_path', '/data')

        self.description = (
            f"Run a container with volume mount:\n"
            f"  - Container name: {self.container_name}\n"
            f"  - Image: {self.image_name}\n"
            f"  - Mount host path: {self.host_path}\n"
            f"  - To container path: {self.container_path}\n"
            f"  - Create host directory if it doesn't exist\n"
            f"  - Run container in background"
        )

        self.hints = [
            f"Create host directory: mkdir -p {self.host_path}",
            f"Run with volume: podman run -d --name {self.container_name} -v {self.host_path}:{self.container_path} {self.image_name} sleep infinity",
            "-v or --volume mounts a host path into the container",
            "Format: -v host_path:container_path",
            "For read-only: -v host_path:container_path:ro",
            f"Verify: podman inspect {self.container_name} | grep -A5 Mounts"
        ]

        return self

    def validate(self):
        """Validate container with volume mount."""
        checks = []
        total_points = 0

        import os

        # Check 1: Host directory exists (3 points)
        if os.path.exists(self.host_path) and os.path.isdir(self.host_path):
            checks.append(ValidationCheck(
                name="host_dir_exists",
                passed=True,
                points=3,
                message=f"Host directory exists"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="host_dir_exists",
                passed=False,
                points=0,
                max_points=3,
                message=f"Host directory {self.host_path} not found"
            ))

        # Check 2: Container exists (4 points)
        if validate_container_exists(self.container_name):
            checks.append(ValidationCheck(
                name="container_exists",
                passed=True,
                points=4,
                message=f"Container exists"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="container_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Container not found"
            ))

        # Check 3: Container is running (5 points)
        if validate_container_running(self.container_name):
            checks.append(ValidationCheck(
                name="container_running",
                passed=True,
                points=5,
                message=f"Container is running"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="container_running",
                passed=False,
                points=0,
                max_points=5,
                message=f"Container is not running"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
