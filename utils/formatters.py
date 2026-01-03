"""
Output formatting utilities for RHCSA Simulator.
"""

from config import settings


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


def colorize(text, color_code):
    """
    Colorize text with ANSI color codes.

    Args:
        text (str): Text to colorize
        color_code (str): ANSI color code

    Returns:
        str: Colorized text (or plain if colors disabled)
    """
    if not settings.USE_COLOR:
        return text
    return f"{color_code}{text}{Colors.RESET}"


def success(text):
    """Format text as success (green)."""
    return colorize(text, Colors.GREEN)


def error(text):
    """Format text as error (red)."""
    return colorize(text, Colors.RED)


def warning(text):
    """Format text as warning (yellow)."""
    return colorize(text, Colors.YELLOW)


def info(text):
    """Format text as info (cyan)."""
    return colorize(text, Colors.CYAN)


def bold(text):
    """Format text as bold."""
    if not settings.USE_COLOR:
        return text
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def dim(text):
    """Format text as dim."""
    if not settings.USE_COLOR:
        return text
    return f"{Colors.DIM}{text}{Colors.RESET}"


def print_header(text, width=None, char='='):
    """
    Print a header with decorative lines.

    Args:
        text (str): Header text
        width (int): Width of header (default: terminal width)
        char (str): Character for decorative lines
    """
    if width is None:
        from utils.helpers import get_terminal_width
        width = get_terminal_width()

    print()
    print(colorize(char * width, Colors.CYAN))
    print(colorize(text.center(width), Colors.BOLD + Colors.CYAN))
    print(colorize(char * width, Colors.CYAN))
    print()


def print_section(text):
    """
    Print a section header.

    Args:
        text (str): Section text
    """
    print()
    print(bold(text))
    print("-" * len(text))


def print_task(task_number, description, max_points=None):
    """
    Print a task description.

    Args:
        task_number (int): Task number
        description (str): Task description
        max_points (int): Maximum points for task
    """
    points_str = f" ({max_points} points)" if max_points else ""
    print(f"\n{bold(f'Task {task_number}:')}{points_str}")
    print(description)


def print_check_result(name, passed, message, points=None, max_points=None):
    """
    Print a validation check result.

    Args:
        name (str): Check name
        passed (bool): Whether check passed
        message (str): Result message
        points (int): Points earned
        max_points (int): Maximum points for this check
    """
    if passed:
        symbol = colorize("✓", Colors.GREEN)
        status = success("PASS")
    else:
        symbol = colorize("✗", Colors.RED)
        status = error("FAIL")

    if points is not None and max_points is not None:
        points_str = f" ({points}/{max_points} points)"
    elif points is not None:
        points_str = f" ({points} points)"
    else:
        points_str = ""

    print(f"  {symbol} {message}{points_str}")


def print_result_summary(passed, score, max_score, percentage):
    """
    Print a task result summary.

    Args:
        passed (bool): Whether task passed
        score (int): Score earned
        max_score (int): Maximum score
        percentage (float): Percentage score
    """
    status = success("PASS") if passed else error("FAIL")
    score_text = f"{score}/{max_score} points ({percentage:.0f}%)"

    print()
    print(f"  Score: {score_text} - {status}")
    print()


def print_table(headers, rows, col_widths=None):
    """
    Print a formatted table.

    Args:
        headers (list): List of header strings
        rows (list): List of row lists
        col_widths (list): Optional list of column widths
    """
    if not rows:
        return

    # Calculate column widths if not provided
    if col_widths is None:
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)  # Add padding

    # Print header
    header_row = "".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(bold(header_row))
    print("-" * sum(col_widths))

    # Print rows
    for row in rows:
        row_str = "".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        print(row_str)


def print_progress_bar(current, total, width=40, prefix="Progress"):
    """
    Print a progress bar.

    Args:
        current (int): Current progress value
        total (int): Total value
        width (int): Width of progress bar
        prefix (str): Prefix text
    """
    if total == 0:
        percentage = 0
    else:
        percentage = int((current / total) * 100)

    filled = int((current / total) * width) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)

    print(f"\r{prefix}: |{bar}| {percentage}% ({current}/{total})", end="", flush=True)


def print_box(text, width=None, padding=1):
    """
    Print text in a box.

    Args:
        text (str): Text to display in box
        width (int): Width of box (default: text length + padding)
        padding (int): Padding around text
    """
    if width is None:
        width = len(text) + (padding * 2) + 2

    top_bottom = "+" + "-" * (width - 2) + "+"
    padding_line = "|" + " " * (width - 2) + "|"
    text_line = "|" + text.center(width - 2) + "|"

    print(top_bottom)
    for _ in range(padding):
        print(padding_line)
    print(text_line)
    for _ in range(padding):
        print(padding_line)
    print(top_bottom)


def print_menu_option(number, text, description=None):
    """
    Print a menu option.

    Args:
        number (int|str): Option number
        text (str): Option text
        description (str): Optional description
    """
    option = bold(f"{number}.")
    if description:
        print(f"  {option} {text}")
        print(f"     {dim(description)}")
    else:
        print(f"  {option} {text}")


def format_category_name(category):
    """
    Format a category name for display.

    Args:
        category (str): Category identifier (e.g., "users_groups")

    Returns:
        str: Formatted name (e.g., "Users & Groups")
    """
    replacements = {
        'users_groups': 'Users & Groups',
        'essential_tools': 'Essential Tools',
        'permissions': 'Permissions & ACLs',
        'lvm': 'LVM (Logical Volume Management)',
        'filesystems': 'File Systems',
        'networking': 'Networking',
        'selinux': 'SELinux',
        'services': 'Services (systemd)',
        'boot': 'Boot Targets',
        'processes': 'Process Management',
        'scheduling': 'Task Scheduling',
        'containers': 'Containers (Podman)'
    }
    return replacements.get(category, category.replace('_', ' ').title())


def format_difficulty(difficulty):
    """
    Format difficulty level for display.

    Args:
        difficulty (str): Difficulty level

    Returns:
        str: Formatted and colored difficulty
    """
    if difficulty == "easy":
        return success("Easy")
    elif difficulty == "exam":
        return warning("Exam")
    elif difficulty == "hard":
        return error("Hard")
    return difficulty.title()


def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('clear' if os.name == 'posix' else 'cls')


def print_divider(char="-", width=None):
    """
    Print a divider line.

    Args:
        char (str): Character to use for divider
        width (int): Width of divider (default: terminal width)
    """
    if width is None:
        from utils.helpers import get_terminal_width
        width = get_terminal_width()
    print(char * width)
