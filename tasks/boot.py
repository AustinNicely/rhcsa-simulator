"""
Boot and system target tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.system_validators import (
    get_default_target, validate_default_target,
    get_grub_timeout, validate_grub_timeout,
    get_grub_cmdline, validate_grub_parameter,
    validate_grub_parameter_value, is_grub_config_updated
)


logger = logging.getLogger(__name__)


@TaskRegistry.register("boot")
class SetDefaultTargetTask(BaseTask):
    """Set systemd default boot target."""

    def __init__(self):
        super().__init__(
            id="boot_target_001",
            category="boot",
            difficulty="easy",
            points=5
        )
        self.target = None

    def generate(self, **params):
        """Generate target change task."""
        targets = [
            ('multi-user.target', 'multi-user (no GUI)'),
            ('graphical.target', 'graphical (GUI)'),
        ]

        choice = params.get('target')
        if choice:
            self.target = choice
            target_desc = next((desc for t, desc in targets if t == choice), choice)
        else:
            self.target, target_desc = random.choice(targets)

        self.description = (
            f"Configure the system boot target:\n"
            f"  - Set the default systemd target to {target_desc}\n"
            f"  - Target: {self.target}\n"
            f"  - Ensure the change persists across reboots"
        )

        self.hints = [
            "Use 'systemctl set-default <target>' to change default target",
            "Use 'systemctl get-default' to verify the current target",
            "Common targets: multi-user.target, graphical.target",
            "You can also use 'systemctl isolate <target>' to switch immediately"
        ]

        return self

    def validate(self):
        """Validate default target setting."""
        checks = []
        total_points = 0

        current_target = get_default_target()

        if current_target == self.target:
            checks.append(ValidationCheck(
                name="default_target",
                passed=True,
                points=5,
                message=f"Default target is correctly set to '{self.target}'"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="default_target",
                passed=False,
                points=0,
                message=f"Default target is '{current_target}', expected '{self.target}'"
            ))

        passed = total_points >= (self.points * 0.8)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("boot")
class ModifyGrubTimeoutTask(BaseTask):
    """Modify GRUB boot menu timeout."""

    def __init__(self):
        super().__init__(
            id="boot_grub_timeout_001",
            category="boot",
            difficulty="medium",
            points=8
        )
        self.timeout = None

    def generate(self, **params):
        """Generate GRUB timeout modification task."""
        self.timeout = params.get('timeout', random.choice([3, 5, 10, 15]))

        self.description = (
            f"Configure the GRUB bootloader:\n"
            f"  - Set the boot menu timeout to {self.timeout} seconds\n"
            f"  - Edit /etc/default/grub\n"
            f"  - Regenerate the GRUB configuration\n"
            f"  - Changes must persist across reboots"
        )

        self.hints = [
            "Edit /etc/default/grub and modify GRUB_TIMEOUT",
            "After editing, run 'grub2-mkconfig -o /boot/grub2/grub.cfg'",
            "On UEFI systems, use '/boot/efi/EFI/redhat/grub.cfg'",
            "Verify changes with 'grep GRUB_TIMEOUT /etc/default/grub'"
        ]

        return self

    def validate(self):
        """Validate GRUB timeout configuration."""
        checks = []
        total_points = 0

        # Check 1: Timeout in /etc/default/grub (4 points)
        current_timeout = get_grub_timeout()
        if current_timeout == self.timeout:
            checks.append(ValidationCheck(
                name="grub_timeout_set",
                passed=True,
                points=4,
                message=f"GRUB timeout correctly set to {self.timeout} seconds"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="grub_timeout_set",
                passed=False,
                points=0,
                message=f"GRUB timeout is {current_timeout}, expected {self.timeout}"
            ))

        # Check 2: GRUB config regenerated (4 points)
        if is_grub_config_updated():
            checks.append(ValidationCheck(
                name="grub_config_exists",
                passed=True,
                points=4,
                message="GRUB configuration file exists"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="grub_config_exists",
                passed=False,
                points=0,
                message="GRUB configuration not found or not regenerated"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("boot")
class AddKernelParameterTask(BaseTask):
    """Add a kernel boot parameter via GRUB."""

    def __init__(self):
        super().__init__(
            id="boot_kernel_param_001",
            category="boot",
            difficulty="medium",
            points=10
        )
        self.parameter = None
        self.parameter_desc = None

    def generate(self, **params):
        """Generate kernel parameter addition task."""
        parameters = [
            ('quiet', 'suppress most boot messages'),
            ('rhgb', 'Red Hat graphical boot'),
            ('rd.break', 'break into emergency shell'),
            ('systemd.unit=multi-user.target', 'boot to multi-user target'),
        ]

        if params.get('parameter'):
            self.parameter = params.get('parameter')
            self.parameter_desc = params.get('description', 'the specified parameter')
        else:
            self.parameter, self.parameter_desc = random.choice(parameters)

        self.description = (
            f"Configure kernel boot parameters:\n"
            f"  - Add '{self.parameter}' to the kernel command line\n"
            f"  - Purpose: {self.parameter_desc}\n"
            f"  - Edit /etc/default/grub (GRUB_CMDLINE_LINUX)\n"
            f"  - Regenerate GRUB configuration\n"
            f"  - Changes must persist across reboots"
        )

        self.hints = [
            "Edit /etc/default/grub",
            f"Add '{self.parameter}' to GRUB_CMDLINE_LINUX line",
            "Separate parameters with spaces",
            "Run 'grub2-mkconfig -o /boot/grub2/grub.cfg' to apply",
            "Verify with 'grep GRUB_CMDLINE_LINUX /etc/default/grub'"
        ]

        return self

    def validate(self):
        """Validate kernel parameter is added."""
        checks = []
        total_points = 0

        # Check if parameter contains '='
        if '=' in self.parameter:
            param_name, param_value = self.parameter.split('=', 1)
            param_exists = validate_grub_parameter_value(param_name, param_value)
        else:
            param_exists = validate_grub_parameter(self.parameter)

        # Check 1: Parameter in GRUB_CMDLINE_LINUX (6 points)
        if param_exists:
            checks.append(ValidationCheck(
                name="kernel_param_added",
                passed=True,
                points=6,
                message=f"Kernel parameter '{self.parameter}' added successfully"
            ))
            total_points += 6
        else:
            current_cmdline = get_grub_cmdline()
            checks.append(ValidationCheck(
                name="kernel_param_added",
                passed=False,
                points=0,
                message=f"Parameter '{self.parameter}' not found in GRUB_CMDLINE_LINUX. Current: {current_cmdline}"
            ))

        # Check 2: GRUB config exists (4 points)
        if is_grub_config_updated():
            checks.append(ValidationCheck(
                name="grub_config_regenerated",
                passed=True,
                points=4,
                message="GRUB configuration updated"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="grub_config_regenerated",
                passed=False,
                points=0,
                message="GRUB configuration needs to be regenerated"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("boot")
class RemoveKernelParameterTask(BaseTask):
    """Remove a kernel boot parameter from GRUB."""

    def __init__(self):
        super().__init__(
            id="boot_kernel_param_remove_001",
            category="boot",
            difficulty="medium",
            points=10
        )
        self.parameter = None

    def generate(self, **params):
        """Generate kernel parameter removal task."""
        parameters = ['quiet', 'rhgb', 'splash']
        self.parameter = params.get('parameter', random.choice(parameters))

        self.description = (
            f"Configure kernel boot parameters:\n"
            f"  - Remove '{self.parameter}' from the kernel command line\n"
            f"  - Edit /etc/default/grub (GRUB_CMDLINE_LINUX)\n"
            f"  - Regenerate GRUB configuration\n"
            f"  - Changes must persist across reboots"
        )

        self.hints = [
            "Edit /etc/default/grub",
            f"Remove '{self.parameter}' from GRUB_CMDLINE_LINUX line",
            "Be careful not to remove other parameters",
            "Run 'grub2-mkconfig -o /boot/grub2/grub.cfg' to apply",
            "Verify with 'grep GRUB_CMDLINE_LINUX /etc/default/grub'"
        ]

        return self

    def validate(self):
        """Validate kernel parameter is removed."""
        checks = []
        total_points = 0

        param_exists = validate_grub_parameter(self.parameter)

        # Check 1: Parameter removed from GRUB_CMDLINE_LINUX (6 points)
        if not param_exists:
            checks.append(ValidationCheck(
                name="kernel_param_removed",
                passed=True,
                points=6,
                message=f"Kernel parameter '{self.parameter}' removed successfully"
            ))
            total_points += 6
        else:
            checks.append(ValidationCheck(
                name="kernel_param_removed",
                passed=False,
                points=0,
                message=f"Parameter '{self.parameter}' still present in GRUB_CMDLINE_LINUX"
            ))

        # Check 2: GRUB config regenerated (4 points)
        if is_grub_config_updated():
            checks.append(ValidationCheck(
                name="grub_config_regenerated",
                passed=True,
                points=4,
                message="GRUB configuration updated"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="grub_config_regenerated",
                passed=False,
                points=0,
                message="GRUB configuration needs to be regenerated"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("boot")
class BootTroubleshootingTask(BaseTask):
    """Boot troubleshooting scenario task."""

    def __init__(self):
        super().__init__(
            id="boot_troubleshoot_001",
            category="boot",
            difficulty="exam",
            points=12
        )
        self.target = 'multi-user.target'
        self.timeout = 5

    def generate(self, **params):
        """Generate boot troubleshooting task."""
        scenarios = [
            {
                'description': 'System boots to graphical interface but should boot to text mode',
                'target': 'multi-user.target',
                'timeout': 5
            },
            {
                'description': 'System boots to text mode but should have GUI',
                'target': 'graphical.target',
                'timeout': 10
            }
        ]

        scenario = params.get('scenario', random.choice(scenarios))
        self.target = scenario['target']
        self.timeout = scenario['timeout']
        scenario_desc = scenario['description']

        self.description = (
            f"Boot Configuration Task:\n"
            f"  Scenario: {scenario_desc}\n"
            f"  \n"
            f"  Required changes:\n"
            f"  - Set default target to: {self.target}\n"
            f"  - Set GRUB timeout to: {self.timeout} seconds\n"
            f"  - Regenerate GRUB configuration\n"
            f"  - All changes must persist across reboots"
        )

        self.hints = [
            "Use 'systemctl set-default <target>' for boot target",
            "Edit /etc/default/grub for GRUB settings",
            "Run 'grub2-mkconfig -o /boot/grub2/grub.cfg'",
            "Verify with 'systemctl get-default' and check /etc/default/grub"
        ]

        return self

    def validate(self):
        """Validate boot troubleshooting solution."""
        checks = []
        total_points = 0

        # Check 1: Default target (5 points)
        if validate_default_target(self.target):
            checks.append(ValidationCheck(
                name="target_fixed",
                passed=True,
                points=5,
                message=f"Default target correctly set to {self.target}"
            ))
            total_points += 5
        else:
            current = get_default_target()
            checks.append(ValidationCheck(
                name="target_fixed",
                passed=False,
                points=0,
                message=f"Target is {current}, expected {self.target}"
            ))

        # Check 2: GRUB timeout (4 points)
        if validate_grub_timeout(self.timeout):
            checks.append(ValidationCheck(
                name="timeout_fixed",
                passed=True,
                points=4,
                message=f"GRUB timeout correctly set to {self.timeout} seconds"
            ))
            total_points += 4
        else:
            current = get_grub_timeout()
            checks.append(ValidationCheck(
                name="timeout_fixed",
                passed=False,
                points=0,
                message=f"Timeout is {current}, expected {self.timeout}"
            ))

        # Check 3: GRUB config regenerated (3 points)
        if is_grub_config_updated():
            checks.append(ValidationCheck(
                name="grub_regenerated",
                passed=True,
                points=3,
                message="GRUB configuration regenerated"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="grub_regenerated",
                passed=False,
                points=0,
                message="GRUB configuration not regenerated"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("boot")
class EmergencyBootTask(BaseTask):
    """Emergency boot and rescue mode knowledge task."""

    def __init__(self):
        super().__init__(
            id="boot_emergency_001",
            category="boot",
            difficulty="exam",
            points=8
        )
        self.target = None

    def generate(self, **params):
        """Generate emergency boot configuration task."""
        self.target = params.get('target', 'emergency.target')

        self.description = (
            f"Configure system for emergency boot scenario:\n"
            f"  - Understand how to boot into emergency mode\n"
            f"  - Know the difference between rescue and emergency targets\n"
            f"  \n"
            f"  For this task:\n"
            f"  - Ensure the system can boot normally (default target set)\n"
            f"  - Document: To boot into emergency mode, add 'systemd.unit=emergency.target'\n"
            f"  - Document: To boot into rescue mode, add 'systemd.unit=rescue.target'\n"
            f"  \n"
            f"  Verify your current default target is set correctly"
        )

        self.hints = [
            "Emergency mode: minimal environment, root filesystem mounted read-only",
            "Rescue mode: more services than emergency, network may be available",
            "At GRUB menu, press 'e' to edit boot parameters temporarily",
            "Add systemd.unit=emergency.target to kernel line for emergency mode",
            "Use 'systemctl get-default' to check current default target"
        ]

        return self

    def validate(self):
        """Validate system can boot normally."""
        checks = []
        total_points = 0

        current_target = get_default_target()

        # Check: System has a valid default target (not emergency/rescue)
        valid_targets = ['multi-user.target', 'graphical.target']

        if current_target in valid_targets:
            checks.append(ValidationCheck(
                name="normal_boot_configured",
                passed=True,
                points=8,
                message=f"System configured for normal boot: {current_target}"
            ))
            total_points += 8
        else:
            checks.append(ValidationCheck(
                name="normal_boot_configured",
                passed=False,
                points=0,
                message=f"Default target is {current_target}, should be multi-user or graphical"
            ))

        passed = total_points >= (self.points * 0.8)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
