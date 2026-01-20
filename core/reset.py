"""
Task reset functionality for RHCSA Simulator.
Provides commands to undo/reset task configurations for retry.
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from validators.safe_executor import execute_safe


logger = logging.getLogger(__name__)


@dataclass
class ResetAction:
    """A single reset action."""
    description: str
    commands: List[List[str]]
    requires_root: bool = True
    dangerous: bool = False


class TaskResetter:
    """
    Provides reset functionality for RHCSA tasks.

    Allows users to undo their configuration attempts and start fresh.
    """

    # Reset actions by task type
    RESET_ACTIONS: Dict[str, Callable[..., ResetAction]] = {}

    @classmethod
    def register_reset(cls, task_type: str):
        """Decorator to register a reset action generator."""
        def decorator(func: Callable[..., ResetAction]):
            cls.RESET_ACTIONS[task_type] = func
            return func
        return decorator

    @classmethod
    def get_reset_action(cls, task_type: str, **params) -> Optional[ResetAction]:
        """Get reset action for a task type."""
        if task_type in cls.RESET_ACTIONS:
            return cls.RESET_ACTIONS[task_type](**params)
        return None

    @classmethod
    def execute_reset(cls, action: ResetAction, dry_run: bool = False) -> Dict:
        """
        Execute a reset action.

        Args:
            action: The reset action to execute
            dry_run: If True, only show what would be done

        Returns:
            Dictionary with results
        """
        results = {
            'success': True,
            'commands_run': [],
            'errors': [],
            'dry_run': dry_run,
        }

        for cmd in action.commands:
            if dry_run:
                results['commands_run'].append(' '.join(cmd))
            else:
                result = execute_safe(cmd, timeout=30)
                results['commands_run'].append({
                    'command': ' '.join(cmd),
                    'success': result.success,
                    'output': result.stdout if result.success else result.stderr,
                })
                if not result.success:
                    results['errors'].append(f"Command failed: {' '.join(cmd)}")
                    # Continue with other commands, but mark as not fully successful
                    results['success'] = False

        return results


# ============================================================================
# RESET ACTION DEFINITIONS
# ============================================================================

@TaskResetter.register_reset('user_create')
def reset_user_create(username: str, **kwargs) -> ResetAction:
    """Reset user creation task."""
    return ResetAction(
        description=f"Remove user '{username}' and their home directory",
        commands=[
            ['userdel', '-r', username],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('user_groups')
def reset_user_groups(username: str, **kwargs) -> ResetAction:
    """Reset user with groups task."""
    return ResetAction(
        description=f"Remove user '{username}' and clean up groups",
        commands=[
            ['userdel', '-r', username],
            # Note: groups are left intact as they might be used elsewhere
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('group_create')
def reset_group_create(groupname: str, **kwargs) -> ResetAction:
    """Reset group creation task."""
    return ResetAction(
        description=f"Remove group '{groupname}'",
        commands=[
            ['groupdel', groupname],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('sudo_config')
def reset_sudo_config(username: str, **kwargs) -> ResetAction:
    """Reset sudo configuration task."""
    return ResetAction(
        description=f"Remove sudo configuration for '{username}'",
        commands=[
            ['rm', '-f', f'/etc/sudoers.d/{username}'],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('selinux_context')
def reset_selinux_context(path: str, context_type: str, **kwargs) -> ResetAction:
    """Reset SELinux context task."""
    return ResetAction(
        description=f"Remove SELinux context mapping for '{path}'",
        commands=[
            ['semanage', 'fcontext', '-d', f'{path}(/.*)?'],
            ['restorecon', '-Rv', path],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('selinux_boolean')
def reset_selinux_boolean(boolean_name: str, **kwargs) -> ResetAction:
    """Reset SELinux boolean task."""
    return ResetAction(
        description=f"Reset SELinux boolean '{boolean_name}' to default",
        commands=[
            ['setsebool', '-P', boolean_name, 'off'],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('selinux_mode')
def reset_selinux_mode(**kwargs) -> ResetAction:
    """Reset SELinux mode task."""
    return ResetAction(
        description="Reset SELinux to Enforcing mode",
        commands=[
            ['setenforce', '1'],
            ['sed', '-i', 's/^SELINUX=.*/SELINUX=enforcing/', '/etc/selinux/config'],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('service_enable')
def reset_service_enable(service: str, **kwargs) -> ResetAction:
    """Reset service enable task."""
    return ResetAction(
        description=f"Stop and disable service '{service}'",
        commands=[
            ['systemctl', 'stop', service],
            ['systemctl', 'disable', service],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('service_disable')
def reset_service_disable(service: str, **kwargs) -> ResetAction:
    """Reset service disable task (re-enable the service)."""
    return ResetAction(
        description=f"Start and enable service '{service}'",
        commands=[
            ['systemctl', 'start', service],
            ['systemctl', 'enable', service],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('directory_setup')
def reset_directory_setup(path: str, **kwargs) -> ResetAction:
    """Reset directory setup task."""
    return ResetAction(
        description=f"Remove directory '{path}'",
        commands=[
            ['rm', '-rf', path],
        ],
        requires_root=True,
        dangerous=True,  # rm -rf is dangerous
    )


@TaskResetter.register_reset('lvm_lv')
def reset_lvm_lv(lv_name: str, vg_name: str, **kwargs) -> ResetAction:
    """Reset LVM logical volume task."""
    return ResetAction(
        description=f"Remove logical volume '{lv_name}' from '{vg_name}'",
        commands=[
            ['umount', f'/dev/{vg_name}/{lv_name}'],  # Might fail if not mounted
            ['lvremove', '-f', f'/dev/{vg_name}/{lv_name}'],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('lvm_vg')
def reset_lvm_vg(vg_name: str, **kwargs) -> ResetAction:
    """Reset LVM volume group task."""
    return ResetAction(
        description=f"Remove volume group '{vg_name}'",
        commands=[
            ['vgremove', '-f', vg_name],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('mount_filesystem')
def reset_mount_filesystem(mountpoint: str, **kwargs) -> ResetAction:
    """Reset filesystem mount task."""
    return ResetAction(
        description=f"Unmount filesystem at '{mountpoint}'",
        commands=[
            ['umount', mountpoint],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('fstab_entry')
def reset_fstab_entry(mountpoint: str, **kwargs) -> ResetAction:
    """Reset fstab entry task."""
    # This is tricky - we need to remove the line from fstab
    return ResetAction(
        description=f"Remove fstab entry for '{mountpoint}'",
        commands=[
            ['sed', '-i', f'\\|{mountpoint}|d', '/etc/fstab'],
        ],
        requires_root=True,
    )


@TaskResetter.register_reset('container_run')
def reset_container_run(name: str, user: str = None, **kwargs) -> ResetAction:
    """Reset container run task."""
    if user:
        # Rootless container
        return ResetAction(
            description=f"Stop and remove container '{name}' for user '{user}'",
            commands=[
                ['su', '-', user, '-c', f'podman stop {name}'],
                ['su', '-', user, '-c', f'podman rm {name}'],
            ],
            requires_root=True,
        )
    else:
        return ResetAction(
            description=f"Stop and remove container '{name}'",
            commands=[
                ['podman', 'stop', name],
                ['podman', 'rm', name],
            ],
            requires_root=True,
        )


class ResetManager:
    """Manages task reset operations."""

    def __init__(self):
        """Initialize reset manager."""
        self.history: List[Dict] = []

    def preview_reset(self, task_type: str, **params) -> Optional[Dict]:
        """
        Preview what a reset would do without executing.

        Returns:
            Dictionary with reset preview or None if not supported
        """
        action = TaskResetter.get_reset_action(task_type, **params)
        if not action:
            return None

        return {
            'task_type': task_type,
            'description': action.description,
            'commands': [' '.join(cmd) for cmd in action.commands],
            'requires_root': action.requires_root,
            'dangerous': action.dangerous,
        }

    def execute_reset(self, task_type: str, confirm: bool = False, **params) -> Dict:
        """
        Execute a reset for a task.

        Args:
            task_type: Type of task to reset
            confirm: Must be True to actually execute
            **params: Parameters for the reset action

        Returns:
            Dictionary with results
        """
        action = TaskResetter.get_reset_action(task_type, **params)
        if not action:
            return {
                'success': False,
                'error': f"No reset action available for task type: {task_type}",
            }

        if action.dangerous and not confirm:
            return {
                'success': False,
                'error': "This reset action is potentially dangerous. Pass confirm=True to execute.",
                'preview': self.preview_reset(task_type, **params),
            }

        if not confirm:
            return {
                'success': False,
                'error': "Reset not confirmed. Pass confirm=True to execute.",
                'preview': self.preview_reset(task_type, **params),
            }

        result = TaskResetter.execute_reset(action)

        # Log to history
        self.history.append({
            'task_type': task_type,
            'params': params,
            'result': result,
        })

        return result

    def get_supported_resets(self) -> List[str]:
        """Get list of supported reset task types."""
        return list(TaskResetter.RESET_ACTIONS.keys())


# Global instance
_reset_manager = None


def get_reset_manager() -> ResetManager:
    """Get global ResetManager instance."""
    global _reset_manager
    if _reset_manager is None:
        _reset_manager = ResetManager()
    return _reset_manager
