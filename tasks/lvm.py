"""
LVM (Logical Volume Management) tasks for RHCSA exam.
"""

import random
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.system_validators import validate_lv_exists, get_lv_size_mb


@TaskRegistry.register("lvm")
class VerifyLVExistsTask(BaseTask):
    """Verify logical volume exists with correct size."""

    def __init__(self):
        super().__init__(
            id="lvm_verify_001",
            category="lvm",
            difficulty="exam",
            points=10
        )
        self.vg_name = None
        self.lv_name = None
        self.lv_size_mb = None

    def generate(self, **params):
        self.vg_name = params.get('vg_name', f'vg_exam{random.randint(1,99)}')
        self.lv_name = params.get('lv_name', f'lv_data{random.randint(1,99)}')
        self.lv_size_mb = params.get('size', random.choice([500, 1000, 2000]))

        self.description = (
            f"Create a logical volume with these specifications:\n"
            f"  - Volume group: {self.vg_name}\n"
            f"  - Logical volume: {self.lv_name}\n"
            f"  - Size: {self.lv_size_mb}MB\n"
            f"\n"
            f"Note: Assume VG already exists or create it if needed"
        )

        self.hints = [
            "Use lvcreate command",
            "Format: lvcreate -L <size>M -n <lv_name> <vg_name>",
            "Verify with 'lvs' command"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0

        if validate_lv_exists(self.vg_name, self.lv_name):
            checks.append(ValidationCheck("lv_exists", True, 5, f"Logical volume exists"))
            total_points += 5

            actual_size = get_lv_size_mb(self.vg_name, self.lv_name)
            tolerance = self.lv_size_mb * 0.05
            if actual_size and abs(actual_size - self.lv_size_mb) <= tolerance:
                checks.append(ValidationCheck("lv_size", True, 5, f"Size correct: ~{actual_size}MB"))
                total_points += 5
            else:
                checks.append(ValidationCheck("lv_size", False, 0, f"Size incorrect: {actual_size}MB (expected {self.lv_size_mb}MB)"))
        else:
            checks.append(ValidationCheck("lv_exists", False, 0, f"Logical volume not found"))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
