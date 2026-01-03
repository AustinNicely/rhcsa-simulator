"""
Command-based validators for users, services, packages, etc.
"""

import logging
from validators.safe_executor import execute_safe


logger = logging.getLogger(__name__)


# User and Group Validators

def validate_user_exists(username):
    """
    Check if a user exists.

    Args:
        username (str): Username to check

    Returns:
        bool: True if user exists
    """
    result = execute_safe(['id', username])
    return result.success


def get_user_uid(username):
    """
    Get UID for a user.

    Args:
        username (str): Username

    Returns:
        str: UID or None if user doesn't exist
    """
    result = execute_safe(['id', '-u', username])
    if result.success:
        return result.stdout.strip()
    return None


def get_user_gid(username):
    """
    Get primary GID for a user.

    Args:
        username (str): Username

    Returns:
        str: GID or None
    """
    result = execute_safe(['id', '-g', username])
    if result.success:
        return result.stdout.strip()
    return None


def get_user_groups(username):
    """
    Get list of groups for a user.

    Args:
        username (str): Username

    Returns:
        list: List of group names
    """
    result = execute_safe(['groups', username])
    if result.success:
        # Output format: "username : group1 group2 group3"
        parts = result.stdout.split(':')
        if len(parts) > 1:
            groups = parts[1].strip().split()
            return groups
    return []


def get_user_shell(username):
    """
    Get user's login shell.

    Args:
        username (str): Username

    Returns:
        str: Shell path or None
    """
    result = execute_safe(['getent', 'passwd', username])
    if result.success:
        # Format: username:x:uid:gid:gecos:home:shell
        fields = result.stdout.split(':')
        if len(fields) >= 7:
            return fields[6].strip()
    return None


def get_user_home(username):
    """
    Get user's home directory.

    Args:
        username (str): Username

    Returns:
        str: Home directory path or None
    """
    result = execute_safe(['getent', 'passwd', username])
    if result.success:
        fields = result.stdout.split(':')
        if len(fields) >= 6:
            return fields[5].strip()
    return None


def validate_group_exists(groupname):
    """
    Check if a group exists.

    Args:
        groupname (str): Group name

    Returns:
        bool: True if group exists
    """
    result = execute_safe(['getent', 'group', groupname])
    return result.success


def get_group_gid(groupname):
    """
    Get GID for a group.

    Args:
        groupname (str): Group name

    Returns:
        str: GID or None
    """
    result = execute_safe(['getent', 'group', groupname])
    if result.success:
        # Format: groupname:x:gid:members
        fields = result.stdout.split(':')
        if len(fields) >= 3:
            return fields[2].strip()
    return None


def get_group_members(groupname):
    """
    Get list of group members.

    Args:
        groupname (str): Group name

    Returns:
        list: List of usernames
    """
    result = execute_safe(['getent', 'group', groupname])
    if result.success:
        fields = result.stdout.split(':')
        if len(fields) >= 4:
            members = fields[3].strip()
            return members.split(',') if members else []
    return []


def check_sudo_access(username):
    """
    Check if user has sudo access.

    Args:
        username (str): Username

    Returns:
        bool: True if user has sudo access
    """
    result = execute_safe(['sudo', '-l', '-U', username])
    # If user has any sudo privileges, command succeeds
    return result.success and 'not allowed' not in result.stdout.lower()


# Service Validators

def validate_service_exists(service_name):
    """
    Check if a systemd service exists.

    Args:
        service_name (str): Service name

    Returns:
        bool: True if service exists
    """
    result = execute_safe(['systemctl', 'cat', service_name])
    return result.success


def validate_service_state(service_name, state='active'):
    """
    Check if service is in a specific state.

    Args:
        service_name (str): Service name
        state (str): Desired state (active, inactive, failed)

    Returns:
        bool: True if service is in specified state
    """
    result = execute_safe(['systemctl', 'is-active', service_name])
    if state == 'active':
        return result.success and result.stdout == 'active'
    elif state == 'inactive':
        return result.stdout == 'inactive'
    elif state == 'failed':
        return result.stdout == 'failed'
    return False


def validate_service_enabled(service_name, enabled=True):
    """
    Check if service is enabled/disabled.

    Args:
        service_name (str): Service name
        enabled (bool): True to check if enabled, False for disabled

    Returns:
        bool: True if service enabled status matches
    """
    result = execute_safe(['systemctl', 'is-enabled', service_name])
    if enabled:
        return result.success and result.stdout == 'enabled'
    else:
        return result.stdout in ['disabled', 'masked']


def get_service_status(service_name):
    """
    Get detailed service status.

    Args:
        service_name (str): Service name

    Returns:
        dict: Service status information
    """
    status_info = {
        'exists': False,
        'active': False,
        'enabled': False,
        'state': 'unknown'
    }

    # Check existence
    if not validate_service_exists(service_name):
        return status_info

    status_info['exists'] = True

    # Check active state
    active_result = execute_safe(['systemctl', 'is-active', service_name])
    status_info['state'] = active_result.stdout
    status_info['active'] = (active_result.stdout == 'active')

    # Check enabled state
    enabled_result = execute_safe(['systemctl', 'is-enabled', service_name])
    status_info['enabled'] = (enabled_result.stdout == 'enabled')

    return status_info


# Process Validators

def validate_process_running(process_name):
    """
    Check if a process is running.

    Args:
        process_name (str): Process name

    Returns:
        bool: True if process is running
    """
    result = execute_safe(['pgrep', '-x', process_name])
    return result.success and len(result.stdout) > 0


def get_process_count(process_name):
    """
    Get count of running processes with given name.

    Args:
        process_name (str): Process name

    Returns:
        int: Number of processes
    """
    result = execute_safe(['pgrep', '-c', '-x', process_name])
    if result.success:
        try:
            return int(result.stdout)
        except ValueError:
            pass
    return 0


# Package Validators

def validate_package_installed(package_name):
    """
    Check if a package is installed (works with RPM-based systems).

    Args:
        package_name (str): Package name

    Returns:
        bool: True if package is installed
    """
    # Try rpm first (RHEL/CentOS/Rocky/Alma)
    result = execute_safe(['rpm', '-q', package_name])
    return result.success


# Network Validators

def get_hostname():
    """
    Get system hostname.

    Returns:
        str: Hostname or None
    """
    result = execute_safe(['hostname'])
    if result.success:
        return result.stdout.strip()
    return None


def validate_hostname(expected_hostname):
    """
    Validate system hostname.

    Args:
        expected_hostname (str): Expected hostname

    Returns:
        bool: True if hostname matches
    """
    actual = get_hostname()
    return actual == expected_hostname


# Boot Target Validators

def get_default_target():
    """
    Get default systemd target.

    Returns:
        str: Default target (e.g., 'multi-user.target')
    """
    result = execute_safe(['systemctl', 'get-default'])
    if result.success:
        return result.stdout.strip()
    return None


def validate_default_target(expected_target):
    """
    Validate default systemd target.

    Args:
        expected_target (str): Expected target

    Returns:
        bool: True if target matches
    """
    actual = get_default_target()
    return actual == expected_target
