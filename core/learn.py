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

KEY FILES TO KNOW:
  /etc/passwd    - User account info (username:x:UID:GID:comment:home:shell)
  /etc/shadow    - Encrypted passwords and aging info
  /etc/group     - Group definitions (groupname:x:GID:members)
  /etc/gshadow   - Group passwords
  /etc/login.defs - Default settings for new users
  /etc/skel/     - Template files copied to new home directories
  /etc/sudoers.d/ - Drop-in sudo configuration files

UID RANGES (RHEL defaults):
  0         - root
  1-999     - System accounts
  1000+     - Regular users
            """,
            "commands": [
                {
                    "name": "Create User with UID",
                    "syntax": "useradd -u <UID> -m <username>",
                    "example": "useradd -u 2500 -m -c 'Exam User' examuser",
                    "flags": {
                        "-u": "Specify user ID (UID)",
                        "-m": "Create home directory",
                        "-M": "Do NOT create home directory",
                        "-g": "Primary group (name or GID)",
                        "-G": "Supplementary groups (comma-separated)",
                        "-s": "Login shell",
                        "-c": "Comment/GECOS field (full name)",
                        "-d": "Home directory path",
                        "-e": "Account expiration date (YYYY-MM-DD)",
                        "-r": "Create system account (UID < 1000)"
                    }
                },
                {
                    "name": "Modify User",
                    "syntax": "usermod [OPTIONS] <username>",
                    "example": "usermod -aG wheel,developers examuser",
                    "flags": {
                        "-aG": "Add to supplementary groups (APPEND - critical!)",
                        "-G": "Set supplementary groups (REPLACES all existing!)",
                        "-L": "Lock account (adds ! to password in shadow)",
                        "-U": "Unlock account",
                        "-s": "Change login shell",
                        "-l": "Change login name",
                        "-d": "Change home directory",
                        "-m": "Move home directory contents (use with -d)",
                        "-e": "Set account expiration date"
                    }
                },
                {
                    "name": "Delete User",
                    "syntax": "userdel [-r] <username>",
                    "example": "userdel -r olduser",
                    "flags": {
                        "userdel user": "Delete user (keeps home directory)",
                        "-r": "Remove home directory and mail spool",
                        "-f": "Force deletion even if user logged in"
                    }
                },
                {
                    "name": "Set Password",
                    "syntax": "passwd <username>",
                    "example": "passwd examuser",
                    "flags": {
                        "passwd": "Change own password",
                        "passwd user": "Change another user's password (root)",
                        "--stdin": "Read password from stdin (scripting)",
                        "-l": "Lock account",
                        "-u": "Unlock account",
                        "-d": "Delete password (passwordless)",
                        "-e": "Expire password (force change on next login)"
                    }
                },
                {
                    "name": "Password Aging (chage)",
                    "syntax": "chage [OPTIONS] <username>",
                    "example": "chage -M 90 -W 7 examuser",
                    "flags": {
                        "-l": "List password aging info",
                        "-d 0": "Force password change on next login",
                        "-M": "Maximum days between password changes",
                        "-m": "Minimum days between password changes",
                        "-W": "Warning days before expiration",
                        "-I": "Inactive days after password expires",
                        "-E": "Account expiration date (YYYY-MM-DD)"
                    }
                },
                {
                    "name": "Configure Sudo Access",
                    "syntax": "echo 'user ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/user",
                    "example": "echo 'examuser ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/examuser && chmod 0440 /etc/sudoers.d/examuser",
                    "flags": {
                        "ALL=(ALL)": "Run as any user on any host",
                        "NOPASSWD:": "No password required",
                        "ALL": "Can run any command",
                        "%groupname": "Apply to group (e.g., %wheel)",
                        "visudo": "Safe way to edit sudoers (checks syntax)"
                    }
                },
                {
                    "name": "Create Group",
                    "syntax": "groupadd -g <GID> <groupname>",
                    "example": "groupadd -g 3000 developers",
                    "flags": {
                        "-g": "Specify group ID (GID)",
                        "-r": "Create system group (GID < 1000)"
                    }
                },
                {
                    "name": "Modify/Delete Group",
                    "syntax": "groupmod / groupdel",
                    "example": "groupmod -n newname oldname",
                    "flags": {
                        "groupmod -n": "Rename group",
                        "groupmod -g": "Change GID",
                        "groupdel": "Delete group (must have no users)"
                    }
                },
                {
                    "name": "View User/Group Info",
                    "syntax": "id / groups / getent",
                    "example": "id examuser && groups examuser",
                    "flags": {
                        "id user": "Show UID, GID, and groups",
                        "groups user": "Show group memberships",
                        "getent passwd user": "Query user from all sources",
                        "getent group grp": "Query group from all sources"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting -m flag -> No home directory created",
                "Using -G without -a -> REMOVES user from ALL existing groups (critical!)",
                "Sudo file wrong permissions (must be 0440 or 0400)",
                "Creating sudo file in /etc/sudoers instead of /etc/sudoers.d/",
                "Not using visudo -> Syntax errors can break ALL sudo access",
                "Forgetting to run 'chage -d 0' when password change on login is required",
                "Using userdel without -r leaves orphaned files",
                "Not verifying with 'id username' after user creation"
            ],
            "exam_tricks": [
                "Exam may specify exact UID - don't let system auto-assign",
                "Multiple supplementary groups - must add ALL of them",
                "Persistent sudo access - must survive reboot (use /etc/sudoers.d/)",
                "User must exist but account might need to be locked (usermod -L)",
                "'Password must change on next login' = chage -d 0 username",
                "Account expiry vs password expiry - they're different!",
                "Always verify with 'id username' and 'sudo -l -U username'"
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

PERMISSION STRUCTURE:
  -rwxrwxrwx = type + owner + group + others

  Type: - (file), d (directory), l (link), b (block), c (char)

NUMERIC VALUES:
  r = 4 (read)
  w = 2 (write)
  x = 1 (execute)

  Example: rwxr-xr-- = 754
    Owner: rwx = 4+2+1 = 7
    Group: r-x = 4+0+1 = 5
    Others: r-- = 4+0+0 = 4

DIRECTORY PERMISSIONS:
  r = list contents (ls)
  w = create/delete files within
  x = access/traverse (cd into)

  Note: Without x, you can't access files even with r!

SPECIAL PERMISSIONS:
  SUID (4) - setuid: File runs as FILE OWNER
  SGID (2) - setgid: File runs as GROUP / Dir inherits group
  Sticky (1) - Only owner can delete their files (e.g., /tmp)

  ls -l shows: s (SUID/SGID with x), S (without x), t (sticky with x), T (without x)
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
                        "Other": "Third digit (r-- = 4)",
                        "-R": "Recursive (apply to all files in directory)"
                    }
                },
                {
                    "name": "Set Permissions (Symbolic)",
                    "syntax": "chmod [ugoa][+-=][rwx] <file>",
                    "example": "chmod u+x,g-w,o=r script.sh",
                    "flags": {
                        "u": "User (owner)",
                        "g": "Group",
                        "o": "Others",
                        "a": "All (u+g+o)",
                        "+": "Add permission",
                        "-": "Remove permission",
                        "=": "Set exact permission"
                    }
                },
                {
                    "name": "Set Special Permissions",
                    "syntax": "chmod <special><perms> <file>",
                    "example": "chmod 2755 /shared/directory",
                    "flags": {
                        "4xxx": "Setuid (4755) - file executes as owner",
                        "2xxx": "Setgid (2755) - file as group / dir inherits group",
                        "1xxx": "Sticky bit (1777) - only owner can delete files",
                        "u+s": "Set SUID (symbolic)",
                        "g+s": "Set SGID (symbolic)",
                        "+t": "Set sticky bit (symbolic)"
                    }
                },
                {
                    "name": "Change Ownership",
                    "syntax": "chown <user>:<group> <file>",
                    "example": "chown apache:apache /var/www/html/index.html",
                    "flags": {
                        "user:group": "Set both owner and group",
                        "user": "Set owner only",
                        "user:": "Set owner, group to user's login group",
                        ":group": "Set group only (or use chgrp)",
                        "-R": "Recursive (for directories)",
                        "--reference=file": "Copy ownership from another file"
                    }
                },
                {
                    "name": "Change Group",
                    "syntax": "chgrp <group> <file>",
                    "example": "chgrp developers /project/code",
                    "flags": {
                        "chgrp group file": "Change group ownership",
                        "-R": "Recursive"
                    }
                },
                {
                    "name": "Set Default Permissions (umask)",
                    "syntax": "umask <mask>",
                    "example": "umask 027",
                    "flags": {
                        "umask": "Display current umask",
                        "umask 022": "Files: 644, Dirs: 755 (default)",
                        "umask 027": "Files: 640, Dirs: 750",
                        "umask 077": "Files: 600, Dirs: 700 (private)",
                        "/etc/bashrc": "Set persistent umask here",
                        "Calculation": "666-umask (files), 777-umask (dirs)"
                    }
                },
                {
                    "name": "Set ACL",
                    "syntax": "setfacl -m u:<user>:<perms> <file>",
                    "example": "setfacl -m u:nginx:rw /var/log/app.log",
                    "flags": {
                        "-m": "Modify ACL (add/change entry)",
                        "u:user:rwx": "User ACL entry",
                        "g:group:rx": "Group ACL entry",
                        "o::r": "Others entry",
                        "-x u:user": "Remove specific ACL entry",
                        "-b": "Remove ALL ACLs",
                        "-R": "Recursive",
                        "-d": "Set DEFAULT ACL (new files inherit, dirs only)",
                        "--set": "Replace all ACLs"
                    }
                },
                {
                    "name": "View ACL",
                    "syntax": "getfacl <file>",
                    "example": "getfacl /data/shared",
                    "flags": {
                        "getfacl file": "Show all ACL entries",
                        "ls -l": "+ at end indicates ACL exists",
                        "mask::": "Maximum effective permissions"
                    }
                },
                {
                    "name": "Default ACLs (Inheritance)",
                    "syntax": "setfacl -d -m u:<user>:<perms> <directory>",
                    "example": "setfacl -d -m u:developer:rwx /projects",
                    "flags": {
                        "-d -m": "Set default ACL (affects NEW files)",
                        "d:u:user:rwx": "Default user ACL",
                        "d:g:group:rx": "Default group ACL",
                        "Note": "Default ACLs ONLY work on directories"
                    }
                }
            ],
            "common_mistakes": [
                "Mixing symbolic and octal notation in same command",
                "Forgetting -R flag for recursive changes on directories",
                "Wrong order in chown (it's user:group, not group:user)",
                "ACL syntax errors (missing colons in u:user:perms)",
                "Not setting DEFAULT ACLs on directories (new files won't inherit)",
                "chmod 755 removes any special permissions - use chmod 2755 to keep SGID",
                "Forgetting x permission on directories (can't cd or access files)",
                "Setting ACL but not checking mask (mask limits effective permissions)",
                "Using chcon instead of setfacl (chcon is for SELinux contexts)"
            ],
            "exam_tricks": [
                "May ask for special permissions - know 4/2/1 prefix (SUID/SGID/Sticky)",
                "SGID on directories = new files inherit group ownership (common exam task)",
                "Sticky bit on shared dirs = users can only delete their own files",
                "ACL + sign in ls -l output indicates ACL exists",
                "Default ACLs (-d) only apply to NEW files/dirs, not existing ones",
                "Verify ACLs with getfacl, not ls -l (ls only shows +)",
                "Capital S or T in ls -l means special permission WITHOUT execute",
                "umask 027 is common for restricting others' access"
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
        },

        "networking": {
            "name": "Networking Configuration",
            "explanation": """
Network configuration in RHEL 8/9 uses NetworkManager and nmcli command.
You must configure static IP addresses, DNS, hostnames, and network interfaces.
The exam tests your ability to use nmcli to create and modify connections,
configure IPv4/IPv6 addressing, set DNS servers, and manage network interfaces.
Understanding connection profiles and device management is critical.
            """,
            "commands": [
                {
                    "name": "Show Network Connections",
                    "syntax": "nmcli connection show",
                    "example": "nmcli connection show",
                    "flags": {
                        "show": "Display all connections",
                        "show <name>": "Show specific connection details",
                        "nmcli con show": "Short form",
                        "nmcli device status": "Show device status"
                    }
                },
                {
                    "name": "Configure Static IP",
                    "syntax": "nmcli con mod <name> ipv4.addresses <ip>/<prefix> ipv4.gateway <gw> ipv4.method manual",
                    "example": "nmcli con mod eth0 ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.method manual",
                    "flags": {
                        "ipv4.addresses": "Set IP address with CIDR notation",
                        "ipv4.gateway": "Set default gateway",
                        "ipv4.method": "manual (static) or auto (DHCP)",
                        "ipv4.dns": "DNS servers (space-separated)"
                    }
                },
                {
                    "name": "Set DNS Servers",
                    "syntax": "nmcli con mod <name> ipv4.dns '<dns1> <dns2>'",
                    "example": "nmcli con mod eth0 ipv4.dns '8.8.8.8 8.8.4.4'",
                    "flags": {
                        "ipv4.dns": "Space-separated DNS IPs (quoted)",
                        "+ipv4.dns": "Add DNS server",
                        "-ipv4.dns": "Remove DNS server"
                    }
                },
                {
                    "name": "Set Hostname",
                    "syntax": "hostnamectl set-hostname <hostname>",
                    "example": "hostnamectl set-hostname server1.example.com",
                    "flags": {
                        "set-hostname": "Set persistent hostname",
                        "status": "Show current hostname",
                        "--static": "Set static hostname",
                        "--transient": "Set transient hostname"
                    }
                },
                {
                    "name": "Activate Connection",
                    "syntax": "nmcli con up <name>",
                    "example": "nmcli con up eth0",
                    "flags": {
                        "up": "Activate connection",
                        "down": "Deactivate connection",
                        "reload": "Reload config files"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting CIDR notation (/24) in IP address",
                "Not quoting DNS servers (space-separated)",
                "Using 'device' instead of 'connection' for config",
                "Forgetting to activate connection after changes",
                "Setting ipv4.method to auto when manual IP is required"
            ],
            "exam_tricks": [
                "Must use nmcli, not editing config files directly",
                "Connection name may differ from interface name",
                "Changes require 'nmcli con up' to take effect",
                "Hostname must be FQDN if specified (server.domain.com)"
            ]
        },

        "filesystems": {
            "name": "File Systems & Mounting",
            "explanation": """
File system management includes creating filesystems, mounting them,
and configuring persistent mounts via /etc/fstab. RHEL 8/9 defaults
to XFS but also supports ext4. You must know mkfs commands, mount/umount,
UUID-based fstab entries, and mount options. The exam tests creating
filesystems on partitions or LVs and making mounts persistent.
            """,
            "commands": [
                {"name": "Create XFS Filesystem", "syntax": "mkfs.xfs <device>", "example": "mkfs.xfs /dev/vgdata/lvdata", "flags": {"mkfs.xfs": "Create XFS filesystem (RHEL default)", "-f": "Force overwrite existing filesystem", "-L": "Set filesystem label"}},
                {"name": "Create ext4 Filesystem", "syntax": "mkfs.ext4 <device>", "example": "mkfs.ext4 /dev/sdb1", "flags": {"mkfs.ext4": "Create ext4 filesystem", "-L": "Set filesystem label", "-m": "Reserved blocks percentage"}},
                {"name": "Mount Filesystem (Temporary)", "syntax": "mount <device> <mountpoint>", "example": "mount /dev/vgdata/lvdata /mnt/data", "flags": {"mount": "Mount filesystem now (not persistent)", "-t": "Specify filesystem type", "-o": "Mount options (ro, rw, noexec, etc.)", "umount": "Unmount filesystem"}},
                {"name": "Get UUID", "syntax": "blkid <device>", "example": "blkid /dev/vgdata/lvdata", "flags": {"blkid": "Show UUID and filesystem type", "-s UUID -o value": "Show only UUID", "lsblk -f": "Alternative to see UUIDs"}},
                {"name": "Add to fstab (Persistent)", "syntax": "echo 'UUID=<uuid> <mount> <type> defaults 0 0' >> /etc/fstab", "example": "echo 'UUID=abc123... /mnt/data xfs defaults 0 0' >> /etc/fstab; mount -a", "flags": {"UUID=": "Use UUID (preferred over device path)", "<mount>": "Mount point directory", "<type>": "Filesystem type (xfs, ext4)", "defaults": "Default mount options", "0 0": "Dump and fsck order", "mount -a": "Mount all fstab entries (test)"}}
            ],
            "common_mistakes": ["Using device path instead of UUID in fstab", "Mount point doesn't exist (must create with mkdir)", "Wrong filesystem type in fstab", "Not testing with 'mount -a' before reboot", "Typos in fstab can prevent boot"],
            "exam_tricks": ["Always use UUID in fstab, not /dev/sdX", "Create mount point directory first (mkdir)", "Test with 'mount -a' to verify fstab syntax", "XFS is default in RHEL 8/9 unless specified otherwise"]
        },

        "boot": {
            "name": "Boot Targets & System Boot",
            "explanation": """
Systemd boot targets replace traditional runlevels in RHEL 8/9.
Common targets are multi-user.target (CLI) and graphical.target (GUI).
You must know how to check the current target, change it temporarily,
and set the default target for future boots. The exam may ask you to
change boot targets or understand the boot process.
            """,
            "commands": [
                {"name": "Show Current Target", "syntax": "systemctl get-default", "example": "systemctl get-default", "flags": {"get-default": "Show default boot target", "list-units --type=target": "Show all active targets", "systemctl isolate": "Switch target now"}},
                {"name": "Set Default Boot Target", "syntax": "systemctl set-default <target>", "example": "systemctl set-default multi-user.target", "flags": {"set-default": "Set persistent default target", "multi-user.target": "CLI mode (runlevel 3)", "graphical.target": "GUI mode (runlevel 5)", "rescue.target": "Single-user rescue mode"}},
                {"name": "Switch Target (Temporary)", "syntax": "systemctl isolate <target>", "example": "systemctl isolate graphical.target", "flags": {"isolate": "Switch to target immediately", "Does not change default target": "Temporary until reboot"}},
                {"name": "Reboot and Power Off", "syntax": "systemctl reboot / poweroff", "example": "systemctl reboot", "flags": {"reboot": "Reboot system", "poweroff": "Shut down system", "halt": "Halt system", "rescue": "Enter rescue mode"}}
            ],
            "common_mistakes": ["Using 'isolate' when permanent change is needed", "Using 'set-default' when immediate change is needed", "Confusing runlevels with targets", "Not verifying change with get-default"],
            "exam_tricks": ["Task says 'boot into' = set-default (permanent)", "Task says 'switch to' = isolate (temporary)", "Multi-user = CLI, Graphical = GUI", "Always verify with 'systemctl get-default'"]
        },

        "containers": {
            "name": "Container Management (Podman)",
            "explanation": """
Podman is the container engine in RHEL 8/9, compatible with Docker commands.
You must know how to run containers, manage images, configure port mapping,
set environment variables, and make containers persistent with systemd.
The exam tests basic podman commands: run, ps, images, exec, and creating
systemd unit files for rootless containers.
            """,
            "commands": [
                {"name": "Run Container", "syntax": "podman run -d --name <name> -p <host>:<container> <image>", "example": "podman run -d --name web -p 8080:80 nginx", "flags": {"-d": "Detached mode (background)", "--name": "Container name", "-p": "Port mapping (host:container)", "-e": "Environment variable", "-v": "Volume mount (host:container)"}},
                {"name": "List Containers", "syntax": "podman ps -a", "example": "podman ps -a", "flags": {"ps": "List running containers", "-a": "Show all (including stopped)", "ps -l": "Show latest container"}},
                {"name": "List Images", "syntax": "podman images", "example": "podman images", "flags": {"images": "List all local images", "pull <image>": "Download image", "rmi <image>": "Remove image"}},
                {"name": "Execute in Container", "syntax": "podman exec -it <container> <command>", "example": "podman exec -it web /bin/bash", "flags": {"exec": "Run command in running container", "-it": "Interactive terminal", "logs <container>": "View container logs"}},
                {"name": "Generate Systemd Unit", "syntax": "podman generate systemd --name <container> --files --new", "example": "podman generate systemd --name web --files --new", "flags": {"generate systemd": "Create systemd unit file", "--name": "Use container name", "--files": "Write to file", "--new": "Create new container on start", "systemctl --user": "User service (rootless)"}}
            ],
            "common_mistakes": ["Forgetting -d flag (container runs in foreground)", "Port already in use on host", "Not pulling image before running", "Wrong systemd path for user services", "Forgetting to enable systemd service"],
            "exam_tricks": ["Rootless containers use systemctl --user", "User systemd units go in ~/.config/systemd/user/", "Must enable AND start systemd service", "Container name must match in systemd commands"]
        },

        "essential_tools": {
            "name": "Essential Command-Line Tools (Files, Find, Tar)",
            "explanation": """
Essential tools include file operations, searching (find, grep),
archiving (tar), compression (gzip, bzip2, xz), and I/O redirection.
The exam tests your ability to efficiently search for files, create
and extract archives, and use links.

FILE TYPES IN LINUX:
  - (regular file)
  d (directory)
  l (symbolic link)
  b (block device)
  c (character device)
  s (socket)
  p (named pipe/FIFO)

HARD LINKS vs SYMBOLIC LINKS:
  Hard Link:
    - Points directly to inode (data blocks)
    - Cannot cross filesystems
    - Cannot link to directories
    - Survives if original deleted (same inode)
    - Same permissions as original

  Symbolic (Soft) Link:
    - Points to filename/path
    - CAN cross filesystems
    - CAN link to directories
    - Breaks if original deleted (dangling link)
    - lrwxrwxrwx permissions (always 777)

TAR COMPRESSION OPTIONS:
  z = gzip  (.tar.gz or .tgz)   - fastest, moderate compression
  j = bzip2 (.tar.bz2)          - slower, better compression
  J = xz    (.tar.xz)           - slowest, best compression
            """,
            "commands": [
                {
                    "name": "Find Files by Name",
                    "syntax": "find <path> -name '<pattern>'",
                    "example": "find /etc -name '*.conf'",
                    "flags": {
                        "-name": "Match filename (case-sensitive, use quotes!)",
                        "-iname": "Match filename (case-insensitive)",
                        "-type f": "Files only",
                        "-type d": "Directories only",
                        "-type l": "Symbolic links only"
                    }
                },
                {
                    "name": "Find Files by Owner/Group",
                    "syntax": "find <path> -user/-group <name>",
                    "example": "find /home -user alice",
                    "flags": {
                        "-user name": "Files owned by user",
                        "-group name": "Files owned by group",
                        "-uid N": "Files with specific UID",
                        "-gid N": "Files with specific GID",
                        "-nouser": "Files with no valid owner (orphaned)",
                        "-nogroup": "Files with no valid group"
                    }
                },
                {
                    "name": "Find Files by Permissions",
                    "syntax": "find <path> -perm <mode>",
                    "example": "find / -perm -4000 2>/dev/null",
                    "flags": {
                        "-perm 755": "Exact permissions (exactly 755)",
                        "-perm -755": "At least these permissions (755 or more)",
                        "-perm /222": "Any of these permissions (u OR g OR o write)",
                        "-perm -4000": "Find SUID files",
                        "-perm -2000": "Find SGID files",
                        "-perm -1000": "Find sticky bit files"
                    }
                },
                {
                    "name": "Find Files by Size/Time",
                    "syntax": "find <path> -size/-mtime <value>",
                    "example": "find /var -size +100M -mtime -7",
                    "flags": {
                        "-size +100M": "Larger than 100MB",
                        "-size -10k": "Smaller than 10KB",
                        "-size 50M": "Exactly 50MB",
                        "-mtime -7": "Modified in last 7 days",
                        "-mtime +30": "Modified more than 30 days ago",
                        "-mmin -60": "Modified in last 60 minutes",
                        "-newer file": "Newer than reference file"
                    }
                },
                {
                    "name": "Find and Execute",
                    "syntax": "find <path> <criteria> -exec <cmd> {} \\;",
                    "example": "find /tmp -name '*.tmp' -exec rm {} \\;",
                    "flags": {
                        "-exec cmd {} \\;": "Run cmd for each file (one at a time)",
                        "-exec cmd {} +": "Run cmd with all files at once (faster)",
                        "-ok cmd {} \\;": "Like -exec but prompts for confirmation",
                        "-delete": "Delete matching files (careful!)",
                        "{}": "Placeholder for found filename"
                    }
                },
                {
                    "name": "Search Text with Grep",
                    "syntax": "grep [OPTIONS] '<pattern>' <file>",
                    "example": "grep -i 'error' /var/log/messages",
                    "flags": {
                        "-i": "Case-insensitive search",
                        "-r": "Recursive search in directories",
                        "-n": "Show line numbers",
                        "-c": "Count matching lines",
                        "-v": "Invert match (lines NOT containing)",
                        "-l": "List filenames only (not content)",
                        "-w": "Match whole words only",
                        "-E": "Extended regex (egrep)",
                        "-A N": "Show N lines after match",
                        "-B N": "Show N lines before match"
                    }
                },
                {
                    "name": "Create Hard Link",
                    "syntax": "ln <target> <linkname>",
                    "example": "ln /data/file.txt /data/file_hardlink.txt",
                    "flags": {
                        "ln target link": "Create hard link to file",
                        "Same inode": "Hard links share same inode number",
                        "Cannot cross FS": "Must be on same filesystem",
                        "No directories": "Cannot hard link directories"
                    }
                },
                {
                    "name": "Create Symbolic Link",
                    "syntax": "ln -s <target> <linkname>",
                    "example": "ln -s /var/log /home/user/logs",
                    "flags": {
                        "-s": "Create symbolic (soft) link",
                        "Can cross FS": "Can link across filesystems",
                        "Can link dirs": "Can create symlinks to directories",
                        "ls -l": "Shows link target: link -> target"
                    }
                },
                {
                    "name": "Copy Files",
                    "syntax": "cp [OPTIONS] <source> <dest>",
                    "example": "cp -a /etc /backup/etc_backup",
                    "flags": {
                        "-r": "Recursive (copy directories)",
                        "-a": "Archive (preserve all: permissions, ownership, timestamps)",
                        "-p": "Preserve permissions and timestamps",
                        "-v": "Verbose (show progress)",
                        "-i": "Interactive (prompt before overwrite)",
                        "-u": "Update (only if source is newer)"
                    }
                },
                {
                    "name": "Create Tar Archive",
                    "syntax": "tar -cvf <archive.tar> <files>",
                    "example": "tar -czvf backup.tar.gz /etc /home",
                    "flags": {
                        "-c": "Create archive",
                        "-v": "Verbose (list files)",
                        "-f": "Specify archive filename (must be last before filename!)",
                        "-z": "Compress with gzip (.tar.gz)",
                        "-j": "Compress with bzip2 (.tar.bz2)",
                        "-J": "Compress with xz (.tar.xz)",
                        "-p": "Preserve permissions",
                        "--exclude='*.log'": "Exclude files matching pattern"
                    }
                },
                {
                    "name": "Extract Tar Archive",
                    "syntax": "tar -xvf <archive.tar> [-C <dir>]",
                    "example": "tar -xzvf backup.tar.gz -C /restore",
                    "flags": {
                        "-x": "Extract archive",
                        "-v": "Verbose",
                        "-f": "Specify archive filename",
                        "-C": "Change to directory before extracting",
                        "-z/-j/-J": "Specify compression (optional, auto-detected)",
                        "--strip-components=N": "Strip N leading directories"
                    }
                },
                {
                    "name": "List Tar Contents",
                    "syntax": "tar -tvf <archive.tar>",
                    "example": "tar -tzvf backup.tar.gz",
                    "flags": {
                        "-t": "List contents (don't extract)",
                        "-v": "Verbose (show permissions, owner, size)",
                        "-f": "Specify archive filename"
                    }
                },
                {
                    "name": "I/O Redirection",
                    "syntax": "command > file / command >> file",
                    "example": "find /etc -name '*.conf' > configs.txt 2>&1",
                    "flags": {
                        ">": "Redirect stdout to file (overwrite)",
                        ">>": "Redirect stdout to file (append)",
                        "2>": "Redirect stderr to file",
                        "2>&1": "Redirect stderr to stdout",
                        "&>": "Redirect both stdout and stderr",
                        "|": "Pipe output to another command",
                        "< file": "Read input from file"
                    }
                }
            ],
            "common_mistakes": [
                "Wrong tar flag order - f must be last before filename",
                "Forgetting quotes in find -name pattern (shell expansion)",
                "Using find -perm 755 when you mean -perm -755 (exact vs minimum)",
                "Creating symlink with relative path (breaks if you move it)",
                "tar -czf backup.tar (forgetting .gz extension with -z)",
                "Extracting tar without -C (extracts to current directory)",
                "Hard linking directories (not allowed)",
                "Forgetting 2>/dev/null to suppress find permission errors"
            ],
            "exam_tricks": [
                "Find SUID files: find / -perm -4000 2>/dev/null",
                "Find SGID files: find / -perm -2000 2>/dev/null",
                "Find files by permission mode: -perm for exact, -perm - for minimum",
                "tar auto-detects compression on extract (no need for -z/-j/-J)",
                "Hard link = same inode, symlink = different inode (check with ls -i)",
                "Find orphaned files: find / -nouser -o -nogroup",
                "Copy preserving everything: cp -a (same as cp -dR --preserve=all)",
                "Remember: -z=gzip, -j=bzip2, -J=xz (lowercase=less compression)"
            ]
        },

        "processes": {
            "name": "Process Management",
            "explanation": """
Process management includes viewing processes, killing processes,
changing priorities, and managing jobs. You must know ps, top, kill,
nice/renice commands.
            """,
            "commands": [
                {"name": "List Processes", "syntax": "ps aux", "example": "ps aux | grep httpd", "flags": {"aux": "All processes"}},
                {"name": "Kill Process", "syntax": "kill <PID>", "example": "kill 1234", "flags": {"kill": "SIGTERM", "-9": "Force"}},
                {"name": "Change Priority", "syntax": "nice -n <value> <command>", "example": "nice -n 10 backup.sh", "flags": {"-n": "Nice value (-20 to 19)"}}
            ],
            "common_mistakes": ["Using kill -9 first", "Confusing nice values"],
            "exam_tricks": ["Find PID: pgrep or pidof", "Nice: -20 = high, 19 = low"]
        },

        "scheduling": {
            "name": "Task Scheduling (cron & at)",
            "explanation": """
Task scheduling uses cron for recurring jobs and at for one-time jobs.
You must know crontab syntax (minute hour day month weekday).
            """,
            "commands": [
                {"name": "Edit Crontab", "syntax": "crontab -e -u <user>", "example": "crontab -e -u alice", "flags": {"-e": "Edit", "-l": "List"}},
                {"name": "Crontab Syntax", "syntax": "MIN HOUR DAY MONTH WEEKDAY COMMAND", "example": "30 2 * * * /usr/local/bin/backup.sh", "flags": {"*": "Every", "*/N": "Every N"}},
                {"name": "One-Time Task", "syntax": "at <time>", "example": "echo '/usr/bin/report.sh' | at 22:00", "flags": {"at": "Schedule once", "atq": "List jobs"}}
            ],
            "common_mistakes": ["Wrong field order", "Forgetting absolute paths"],
            "exam_tricks": ["Crontab: MIN HOUR DAY MONTH WEEKDAY", "0 2 * * * = 2 AM daily"]
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
