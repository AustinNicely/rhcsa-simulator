"""
Learn Mode - Instructional content for RHCSA topics.
Provides explanations, commands, and common mistakes for each topic.
"""

import logging
from utils import formatters as fmt
from utils.helpers import confirm_action


logger = logging.getLogger(__name__)


class LearnContent:
    """
    Educational content for RHCSA topics.
    Each topic includes: explanation, commands, examples, and common mistakes.
    """

    TOPICS = {
        "users_groups": {
            "name": "Users & Groups Management",
            "explanation": """
User and group management is fundamental to Linux system administration.
You'll need to create users with specific UIDs, assign them to groups,
configure sudo access, and manage user properties. The exam tests your
ability to use useradd, usermod, groupadd, and sudo configuration.
Understanding /etc/passwd, /etc/group, and /etc/sudoers is critical.
            """,
            "commands": [
                {
                    "name": "Create User with UID",
                    "syntax": "useradd -u <UID> -m <username>",
                    "example": "useradd -u 2500 -m examuser",
                    "flags": {
                        "-u": "Specify user ID (UID)",
                        "-m": "Create home directory",
                        "-g": "Primary group",
                        "-G": "Supplementary groups (comma-separated)",
                        "-s": "Login shell"
                    }
                },
                {
                    "name": "Modify User",
                    "syntax": "usermod [OPTIONS] <username>",
                    "example": "usermod -aG wheel,developers examuser",
                    "flags": {
                        "-aG": "Add to supplementary groups (append)",
                        "-G": "Set supplementary groups (replace)",
                        "-L": "Lock account",
                        "-U": "Unlock account",
                        "-s": "Change shell"
                    }
                },
                {
                    "name": "Configure Sudo Access",
                    "syntax": "echo 'user ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/user",
                    "example": "echo 'examuser ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/examuser",
                    "flags": {
                        "ALL=(ALL)": "Run as any user",
                        "NOPASSWD:": "No password required",
                        "ALL": "Can run any command"
                    }
                },
                {
                    "name": "Create Group",
                    "syntax": "groupadd -g <GID> <groupname>",
                    "example": "groupadd -g 3000 developers",
                    "flags": {
                        "-g": "Specify group ID (GID)"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting -m flag → No home directory created",
                "Using -G without -a → Removes user from existing groups",
                "Sudo file wrong permissions (must be 0440)",
                "Creating sudo file in /etc/sudoers instead of /etc/sudoers.d/",
                "Not using visudo → Syntax errors break sudo"
            ],
            "exam_tricks": [
                "Exam may specify exact UID - don't let system auto-assign",
                "Multiple supplementary groups - must add ALL of them",
                "Persistent sudo access - must survive reboot",
                "User must exist but account might need to be locked"
            ]
        },

        "permissions": {
            "name": "File Permissions & ACLs",
            "explanation": """
Linux permissions control file access using owner, group, and other.
Special permissions (setuid, setgid, sticky) add advanced functionality.
ACLs (Access Control Lists) provide fine-grained access control beyond
traditional permissions. The exam tests chmod, chown, setfacl, and
understanding of permission inheritance and special bits.
            """,
            "commands": [
                {
                    "name": "Set Permissions (Octal)",
                    "syntax": "chmod <octal> <file>",
                    "example": "chmod 755 /usr/local/bin/myscript",
                    "flags": {
                        "4": "Read permission",
                        "2": "Write permission",
                        "1": "Execute permission",
                        "Owner": "First digit (rwx = 7)",
                        "Group": "Second digit (r-x = 5)",
                        "Other": "Third digit (r-- = 4)"
                    }
                },
                {
                    "name": "Set Special Permissions",
                    "syntax": "chmod <special><perms> <file>",
                    "example": "chmod 2755 /shared/directory",
                    "flags": {
                        "4": "Setuid (4755) - runs as owner",
                        "2": "Setgid (2755) - runs as group/inherits group",
                        "1": "Sticky bit (1777) - only owner can delete"
                    }
                },
                {
                    "name": "Change Ownership",
                    "syntax": "chown <user>:<group> <file>",
                    "example": "chown apache:apache /var/www/html/index.html",
                    "flags": {
                        "user:group": "Set both owner and group",
                        "user:": "Set owner, group unchanged",
                        ":group": "Set group, owner unchanged",
                        "-R": "Recursive (for directories)"
                    }
                },
                {
                    "name": "Set ACL",
                    "syntax": "setfacl -m u:<user>:<perms> <file>",
                    "example": "setfacl -m u:nginx:rw- /var/log/app.log",
                    "flags": {
                        "-m": "Modify ACL",
                        "u:user:perms": "User ACL entry",
                        "g:group:perms": "Group ACL entry",
                        "-R": "Recursive",
                        "-d": "Set default ACL (directories)"
                    }
                }
            ],
            "common_mistakes": [
                "Mixing symbolic and octal notation",
                "Forgetting recursive flag for directories",
                "Wrong order in chown (user:group, not group:user)",
                "ACL syntax errors (missing colons)",
                "Not setting default ACLs on directories"
            ],
            "exam_tricks": [
                "May ask for special permissions - know 4/2/1 prefix",
                "ACLs on directories - don't forget -d for inheritance",
                "Group ownership separate from user ownership",
                "Verify with getfacl, not just ls -l"
            ]
        },

        "services": {
            "name": "Service Management (systemd)",
            "explanation": """
Systemd is the init system and service manager in RHEL 8/9.
You must know how to start, stop, enable, disable, and check service status.
Understanding the difference between 'start' (now) and 'enable' (at boot)
is crucial. The exam tests service manipulation, unit file creation,
and boot target management.
            """,
            "commands": [
                {
                    "name": "Start Service (Immediately)",
                    "syntax": "systemctl start <service>",
                    "example": "systemctl start httpd",
                    "flags": {
                        "start": "Start service now (doesn't survive reboot)",
                        "stop": "Stop service now",
                        "restart": "Stop then start",
                        "reload": "Reload config without stopping"
                    }
                },
                {
                    "name": "Enable Service (At Boot)",
                    "syntax": "systemctl enable <service>",
                    "example": "systemctl enable httpd",
                    "flags": {
                        "enable": "Start at boot (doesn't start now)",
                        "disable": "Don't start at boot",
                        "enable --now": "Enable AND start immediately"
                    }
                },
                {
                    "name": "Check Service Status",
                    "syntax": "systemctl status <service>",
                    "example": "systemctl status sshd",
                    "flags": {
                        "status": "Show current status and recent logs",
                        "is-active": "Check if running (active/inactive)",
                        "is-enabled": "Check if enabled at boot"
                    }
                },
                {
                    "name": "Mask Service (Prevent Start)",
                    "syntax": "systemctl mask <service>",
                    "example": "systemctl mask postfix",
                    "flags": {
                        "mask": "Completely prevent service from starting",
                        "unmask": "Remove mask"
                    }
                }
            ],
            "common_mistakes": [
                "Only starting service (forgetting to enable)",
                "Only enabling service (forgetting to start)",
                "Using service name without .service suffix sometimes needed",
                "Not reloading systemd after editing unit files",
                "Checking wrong service name"
            ],
            "exam_tricks": [
                "Task says 'configure to start at boot' = enable + start",
                "Service might already be masked - must unmask first",
                "May need to reload daemon: systemctl daemon-reload",
                "Check both is-active AND is-enabled"
            ]
        },

        "selinux": {
            "name": "SELinux Security",
            "explanation": """
SELinux (Security-Enhanced Linux) provides mandatory access control.
You must understand contexts (user:role:type:level), booleans, and modes.
The exam tests setting file contexts with semanage/restorecon,
toggling booleans with setsebool, and changing SELinux modes.
Always make changes persistent!
            """,
            "commands": [
                {
                    "name": "Set File Context (Persistent)",
                    "syntax": "semanage fcontext -a -t <type> '<path>(/.*)?' && restorecon -Rv <path>",
                    "example": "semanage fcontext -a -t httpd_sys_content_t '/web(/.*)?'\nrestorecon -Rv /web",
                    "flags": {
                        "-a": "Add policy rule",
                        "-t": "Set type context",
                        "'<path>(/.*)?'": "Regex for path and subdirs",
                        "restorecon -Rv": "Apply the context now"
                    }
                },
                {
                    "name": "Set Boolean (Persistent)",
                    "syntax": "setsebool -P <boolean> on|off",
                    "example": "setsebool -P httpd_can_network_connect on",
                    "flags": {
                        "-P": "Make change persistent (CRITICAL!)",
                        "on": "Enable boolean",
                        "off": "Disable boolean"
                    }
                },
                {
                    "name": "Change SELinux Mode",
                    "syntax": "setenforce 0|1 && edit /etc/selinux/config",
                    "example": "setenforce 0\nvi /etc/selinux/config (set SELINUX=permissive)",
                    "flags": {
                        "0": "Permissive mode (now)",
                        "1": "Enforcing mode (now)",
                        "/etc/selinux/config": "Persistent setting",
                        "SELINUX=": "enforcing, permissive, or disabled"
                    }
                },
                {
                    "name": "Check Context",
                    "syntax": "ls -Z <file>",
                    "example": "ls -Zd /var/www/html",
                    "flags": {
                        "-Z": "Show SELinux context",
                        "getenforce": "Show current mode",
                        "getsebool -a": "List all booleans"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting -P flag on setsebool (not persistent!)",
                "Not running restorecon after semanage",
                "Wrong regex pattern in semanage (missing (/.*)?)",
                "Setting mode without editing /etc/selinux/config",
                "Using chcon instead of semanage (not persistent)"
            ],
            "exam_tricks": [
                "Exam always wants persistent changes - use -P and semanage",
                "File context needs BOTH semanage AND restorecon",
                "Boolean might already be set but not persistent",
                "Context format is user:role:type:level (you usually change type)"
            ]
        },

        "lvm": {
            "name": "LVM (Logical Volume Management)",
            "explanation": """
LVM provides flexible disk management with physical volumes (PV),
volume groups (VG), and logical volumes (LV). The hierarchy is:
Disk → PV → VG → LV → Filesystem. You must know creation, extension,
and reduction operations. The exam tests your ability to create the
full LVM stack and resize volumes.
            """,
            "commands": [
                {
                    "name": "Create Physical Volume",
                    "syntax": "pvcreate <device>",
                    "example": "pvcreate /dev/sdb",
                    "flags": {
                        "/dev/sdX": "Block device to use",
                        "pvdisplay": "Show PV details",
                        "pvs": "List PVs (short)"
                    }
                },
                {
                    "name": "Create Volume Group",
                    "syntax": "vgcreate <vgname> <pv>",
                    "example": "vgcreate vgdata /dev/sdb",
                    "flags": {
                        "vgname": "Name for volume group",
                        "pv": "Physical volume(s) to include",
                        "vgdisplay": "Show VG details",
                        "vgs": "List VGs (short)"
                    }
                },
                {
                    "name": "Create Logical Volume",
                    "syntax": "lvcreate -n <lvname> -L <size> <vgname>",
                    "example": "lvcreate -n lvdata -L 500M vgdata",
                    "flags": {
                        "-n": "Logical volume name",
                        "-L": "Size (M, G, T)",
                        "-l": "Size in extents (e.g., -l 100%FREE)",
                        "lvdisplay": "Show LV details",
                        "lvs": "List LVs (short)"
                    }
                },
                {
                    "name": "Extend Logical Volume",
                    "syntax": "lvextend -L +<size> <lv_path> && resize2fs/xfs_growfs",
                    "example": "lvextend -L +1G /dev/vgdata/lvdata\nxfs_growfs /dev/vgdata/lvdata",
                    "flags": {
                        "-L +size": "Increase by size",
                        "-L size": "Set to absolute size",
                        "-r": "Resize filesystem automatically",
                        "resize2fs": "For ext4 filesystems",
                        "xfs_growfs": "For XFS filesystems"
                    }
                }
            ],
            "common_mistakes": [
                "Wrong order: must create PV → VG → LV",
                "Forgetting to resize filesystem after extending LV",
                "Using wrong filesystem resize command (ext4 vs XFS)",
                "Not using -r flag to auto-resize",
                "Insufficient space in VG for LV"
            ],
            "exam_tricks": [
                "Exam specifies exact size - watch units (M vs MB vs MiB)",
                "May ask to extend existing LV (not create new)",
                "Filesystem resize is separate step (unless -r flag)",
                "Path is /dev/vgname/lvname or /dev/mapper/vgname-lvname"
            ]
        }
    }

    @classmethod
    def get_topic(cls, category):
        """Get learning content for a topic."""
        return cls.TOPICS.get(category)

    @classmethod
    def get_all_topics(cls):
        """Get all available learning topics."""
        return list(cls.TOPICS.keys())


class LearnMode:
    """
    Learn Mode interface - displays instructional content.
    """

    def __init__(self):
        """Initialize learn mode."""
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start learn mode - let user choose topic."""
        while True:
            fmt.clear_screen()
            fmt.print_header("LEARN MODE - Choose a Topic")

            topics = LearnContent.get_all_topics()

            # Display topics
            for i, topic_key in enumerate(sorted(topics), 1):
                topic = LearnContent.get_topic(topic_key)
                fmt.print_menu_option(i, topic['name'])

            fmt.print_menu_option('Q', "Back to Main Menu")

            choice = input("\nSelect topic (number or Q): ").strip()

            if choice.lower() == 'q':
                return

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(topics):
                    topic_key = sorted(topics)[idx]
                    self._display_topic(topic_key)
                else:
                    print(fmt.error("Invalid selection"))
                    input("Press Enter to continue...")
            except ValueError:
                print(fmt.error("Please enter a number or Q"))
                input("Press Enter to continue...")

    def _display_topic(self, topic_key):
        """Display learning content for a topic."""
        topic = LearnContent.get_topic(topic_key)

        fmt.clear_screen()
        fmt.print_header(f"LEARN: {topic['name']}")

        # Explanation
        print(fmt.bold("📖 CONCEPT OVERVIEW:"))
        print(topic['explanation'].strip())
        print()

        # Commands
        print(fmt.bold("💻 ESSENTIAL COMMANDS:"))
        print("=" * 70)
        for cmd in topic['commands']:
            print()
            print(fmt.success(f"▸ {cmd['name']}"))
            print()
            print(fmt.bold("  Syntax:"))
            print(f"    {fmt.info(cmd['syntax'])}")
            print()
            print(fmt.bold("  Example:"))
            print(f"    $ {cmd['example']}")
            print()
            print(fmt.bold("  Flags:"))
            for flag, description in cmd['flags'].items():
                print(f"    {fmt.warning(flag):20} → {description}")
            print()

        # Common Mistakes
        print("=" * 70)
        print(fmt.bold("⚠️  COMMON MISTAKES:"))
        for i, mistake in enumerate(topic['common_mistakes'], 1):
            print(f"  {i}. {fmt.error('✗')} {mistake}")
        print()

        # Exam Tricks
        print(fmt.bold("🎯 EXAM TIPS:"))
        for i, trick in enumerate(topic['exam_tricks'], 1):
            print(f"  {i}. {fmt.warning('!')} {trick}")
        print()

        # Navigate
        print("=" * 70)
        choice = input("\n[P] Practice this topic  [B] Back to topics  [Q] Main menu: ").strip().lower()

        if choice == 'p':
            # Launch practice mode for this topic
            from core.practice import PracticeSession
            session = PracticeSession()
            session.category = topic_key
            session.difficulty = 'exam'
            session.task_count = 3

            tasks_module = __import__(f'tasks.{topic_key}', fromlist=[''])
            from tasks.registry import TaskRegistry
            TaskRegistry.initialize()

            tasks = TaskRegistry.get_practice_tasks(topic_key, 'exam', 3)
            if tasks:
                for i, task in enumerate(tasks, 1):
                    session._practice_task(task, i, len(tasks))
            else:
                print(fmt.warning("No practice tasks available for this topic yet."))
                input("Press Enter to continue...")


def run_learn_mode():
    """Run learn mode (convenience function)."""
    mode = LearnMode()
    mode.start()
