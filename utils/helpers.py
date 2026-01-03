"""
Helper utility functions for RHCSA Simulator.
"""

import os
import sys
import uuid
from datetime import timedelta


def check_root():
    """
    Check if the script is running with root privileges.

    Returns:
        bool: True if running as root, False otherwise
    """
    return os.geteuid() == 0


def require_root():
    """
    Require root privileges to continue. Exit if not root.
    """
    if not check_root():
        print("Error: This application requires root privileges.")
        print("Please run with: sudo rhcsa-simulator")
        sys.exit(1)


def generate_id(prefix=""):
    """
    Generate a unique ID with optional prefix.

    Args:
        prefix (str): Optional prefix for the ID

    Returns:
        str: Unique ID string
    """
    unique_id = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def format_time(seconds):
    """
    Format seconds into human-readable time string.

    Args:
        seconds (int): Number of seconds

    Returns:
        str: Formatted time string (e.g., "2h 30m 15s")
    """
    if seconds < 0:
        return "0s"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_timedelta(td):
    """
    Format a timedelta into human-readable string.

    Args:
        td (timedelta): Time delta object

    Returns:
        str: Formatted time string
    """
    total_seconds = int(td.total_seconds())
    return format_time(total_seconds)


def parse_percentage(value):
    """
    Parse a percentage value from various formats.

    Args:
        value: String or number representing a percentage

    Returns:
        float: Percentage as decimal (0.0-1.0)
    """
    if isinstance(value, (int, float)):
        if value > 1:
            return value / 100.0
        return float(value)

    if isinstance(value, str):
        value = value.strip().rstrip('%')
        try:
            num = float(value)
            if num > 1:
                return num / 100.0
            return num
        except ValueError:
            return 0.0

    return 0.0


def confirm_action(prompt, default=False):
    """
    Ask user for confirmation.

    Args:
        prompt (str): Confirmation prompt
        default (bool): Default value if user just presses Enter

    Returns:
        bool: True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        response = input(prompt + suffix).strip().lower()
        if response == '':
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")


def get_terminal_width():
    """
    Get the current terminal width.

    Returns:
        int: Terminal width in characters (default 80)
    """
    try:
        import shutil
        return shutil.get_terminal_size((80, 20)).columns
    except:
        return 80


def truncate_string(text, max_length, suffix="..."):
    """
    Truncate a string to maximum length.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pluralize(count, singular, plural=None):
    """
    Return singular or plural form based on count.

    Args:
        count (int): Count value
        singular (str): Singular form
        plural (str): Plural form (default: singular + 's')

    Returns:
        str: Appropriate form
    """
    if plural is None:
        plural = singular + 's'
    return singular if count == 1 else plural


def format_list(items, conjunction="and"):
    """
    Format a list of items as a comma-separated string with conjunction.

    Args:
        items (list): List of items
        conjunction (str): Conjunction word (default: "and")

    Returns:
        str: Formatted string
    """
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return ", ".join(str(item) for item in items[:-1]) + f", {conjunction} {items[-1]}"


def safe_divide(numerator, denominator, default=0.0):
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero

    Returns:
        float: Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def clamp(value, min_val, max_val):
    """
    Clamp a value between minimum and maximum.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))
