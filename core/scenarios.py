"""
Scenario-based chained tasks for RHCSA Simulator.
Creates realistic multi-step scenarios that chain related tasks together.
"""

import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from tasks.registry import TaskRegistry
from core.validator import ValidationResult, ValidationCheck


logger = logging.getLogger(__name__)


@dataclass
class ScenarioStep:
    """A single step in a scenario."""
    step_number: int
    description: str
    task_type: str
    task_params: Dict
    points: int
    hints: List[str] = field(default_factory=list)
    depends_on: List[int] = field(default_factory=list)  # Step numbers this depends on


@dataclass
class Scenario:
    """A complete scenario with multiple steps."""
    id: str
    title: str
    description: str
    difficulty: str
    category: str
    total_points: int
    time_estimate_minutes: int
    steps: List[ScenarioStep]
    context: str  # Real-world context
    objectives: List[str]

    def get_step(self, step_number: int) -> Optional[ScenarioStep]:
        """Get a specific step by number."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None


class ScenarioRegistry:
    """Registry of available scenarios."""

    _scenarios: Dict[str, Callable[[], Scenario]] = {}

    @classmethod
    def register(cls, scenario_id: str):
        """Decorator to register a scenario generator."""
        def decorator(func: Callable[[], Scenario]):
            cls._scenarios[scenario_id] = func
            return func
        return decorator

    @classmethod
    def get_scenario(cls, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        if scenario_id in cls._scenarios:
            return cls._scenarios[scenario_id]()
        return None

    @classmethod
    def get_all_scenarios(cls) -> List[Dict]:
        """Get list of all available scenarios."""
        scenarios = []
        for scenario_id, generator in cls._scenarios.items():
            scenario = generator()
            scenarios.append({
                'id': scenario_id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'total_points': scenario.total_points,
                'time_estimate': scenario.time_estimate_minutes,
                'step_count': len(scenario.steps),
            })
        return scenarios

    @classmethod
    def get_scenarios_by_category(cls, category: str) -> List[Scenario]:
        """Get scenarios filtered by category."""
        return [
            gen() for gen in cls._scenarios.values()
            if gen().category == category
        ]


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

@ScenarioRegistry.register("web_server_setup")
def create_web_server_scenario() -> Scenario:
    """Create a complete web server setup scenario."""
    server_num = random.randint(1, 99)
    username = f"webadmin{server_num}"
    web_dir = f"/srv/www{server_num}"

    return Scenario(
        id="web_server_setup",
        title="Web Server Deployment",
        description="Set up a complete Apache web server with proper user, directory, permissions, and SELinux configuration.",
        difficulty="exam",
        category="integrated",
        total_points=35,
        time_estimate_minutes=20,
        context="Your company needs a new internal web server for the development team. "
                "You must configure everything from scratch following security best practices.",
        objectives=[
            "Create a dedicated service user",
            "Set up document root directory",
            "Configure proper permissions",
            "Set correct SELinux contexts",
            "Enable and start the web service",
        ],
        steps=[
            ScenarioStep(
                step_number=1,
                description=f"Create a user '{username}' to manage web content:\n"
                           f"  - UID: 1800\n"
                           f"  - Primary group: apache\n"
                           f"  - Home directory: {web_dir}\n"
                           f"  - Shell: /bin/bash",
                task_type="user_create",
                task_params={'username': username, 'uid': 1800, 'group': 'apache', 'home': web_dir},
                points=8,
                hints=[
                    "Use useradd with -u, -g, -d, and -m flags",
                    "The apache group should already exist if httpd is installed",
                ],
            ),
            ScenarioStep(
                step_number=2,
                description=f"Create the web document root directory:\n"
                           f"  - Path: {web_dir}/html\n"
                           f"  - Owner: {username}\n"
                           f"  - Group: apache\n"
                           f"  - Permissions: 2775 (setgid)",
                task_type="directory_setup",
                task_params={'path': f'{web_dir}/html', 'owner': username, 'group': 'apache', 'mode': '2775'},
                points=6,
                hints=[
                    "mkdir -p to create nested directories",
                    "chown user:group for ownership",
                    "chmod 2775 for setgid + rwxrwxr-x",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=3,
                description=f"Configure SELinux context for the web directory:\n"
                           f"  - Set type: httpd_sys_content_t\n"
                           f"  - Apply to: {web_dir}(/.*)?",
                task_type="selinux_context",
                task_params={'path': web_dir, 'context_type': 'httpd_sys_content_t'},
                points=8,
                hints=[
                    "semanage fcontext -a -t httpd_sys_content_t 'path(/.*)?'",
                    "restorecon -Rv path",
                ],
                depends_on=[2],
            ),
            ScenarioStep(
                step_number=4,
                description="Enable SELinux boolean for home directory access:\n"
                           "  - Boolean: httpd_enable_homedirs\n"
                           "  - Value: on\n"
                           "  - Make persistent",
                task_type="selinux_boolean",
                task_params={'boolean': 'httpd_enable_homedirs', 'value': 'on'},
                points=5,
                hints=[
                    "setsebool -P httpd_enable_homedirs on",
                ],
            ),
            ScenarioStep(
                step_number=5,
                description="Configure the httpd service:\n"
                           "  - Start the service\n"
                           "  - Enable at boot",
                task_type="service_enable",
                task_params={'service': 'httpd'},
                points=5,
                hints=[
                    "systemctl enable --now httpd",
                ],
                depends_on=[3, 4],
            ),
            ScenarioStep(
                step_number=6,
                description=f"Configure sudo access for {username}:\n"
                           f"  - Allow running systemctl commands\n"
                           f"  - No password required",
                task_type="sudo_config",
                task_params={'username': username, 'commands': '/usr/bin/systemctl'},
                points=3,
                hints=[
                    f"Create /etc/sudoers.d/{username}",
                    f"{username} ALL=(ALL) NOPASSWD: /usr/bin/systemctl",
                ],
                depends_on=[1],
            ),
        ],
    )


@ScenarioRegistry.register("samba_share_setup")
def create_samba_share_scenario() -> Scenario:
    """Create a Samba file share scenario."""
    share_name = f"projects{random.randint(1, 99)}"
    share_dir = f"/srv/samba/{share_name}"
    group_name = "smbusers"

    return Scenario(
        id="samba_share_setup",
        title="Samba Share Configuration",
        description="Configure a Samba share for team collaboration with proper access controls.",
        difficulty="exam",
        category="integrated",
        total_points=32,
        time_estimate_minutes=18,
        context="The development team needs a shared directory accessible via Samba "
                "for cross-platform file sharing. Security and proper access control are required.",
        objectives=[
            "Create shared directory structure",
            "Configure group-based access",
            "Set SELinux contexts for Samba",
            "Enable Samba service",
        ],
        steps=[
            ScenarioStep(
                step_number=1,
                description=f"Create a group for Samba users:\n"
                           f"  - Group name: {group_name}\n"
                           f"  - GID: 3000",
                task_type="group_create",
                task_params={'groupname': group_name, 'gid': 3000},
                points=4,
                hints=["groupadd -g 3000 smbusers"],
            ),
            ScenarioStep(
                step_number=2,
                description=f"Create two users for the share:\n"
                           f"  - smbuser1 (UID: 3001) in group {group_name}\n"
                           f"  - smbuser2 (UID: 3002) in group {group_name}",
                task_type="multi_user_create",
                task_params={'users': [
                    {'username': 'smbuser1', 'uid': 3001, 'group': group_name},
                    {'username': 'smbuser2', 'uid': 3002, 'group': group_name},
                ]},
                points=6,
                hints=["Create each user with useradd -u UID -g group username"],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=3,
                description=f"Create the share directory:\n"
                           f"  - Path: {share_dir}\n"
                           f"  - Group: {group_name}\n"
                           f"  - Permissions: 2770",
                task_type="directory_setup",
                task_params={'path': share_dir, 'group': group_name, 'mode': '2770'},
                points=6,
                hints=[
                    "mkdir -p for nested directories",
                    "chgrp for group ownership",
                    "chmod 2770 for setgid + rwxrwx---",
                ],
            ),
            ScenarioStep(
                step_number=4,
                description=f"Set SELinux context for Samba:\n"
                           f"  - Path: {share_dir}\n"
                           f"  - Type: samba_share_t",
                task_type="selinux_context",
                task_params={'path': share_dir, 'context_type': 'samba_share_t'},
                points=8,
                hints=[
                    f"semanage fcontext -a -t samba_share_t '{share_dir}(/.*)?'",
                    f"restorecon -Rv {share_dir}",
                ],
                depends_on=[3],
            ),
            ScenarioStep(
                step_number=5,
                description="Enable SELinux boolean for Samba home directories:\n"
                           "  - Boolean: samba_enable_home_dirs\n"
                           "  - Make persistent",
                task_type="selinux_boolean",
                task_params={'boolean': 'samba_enable_home_dirs', 'value': 'on'},
                points=4,
                hints=["setsebool -P samba_enable_home_dirs on"],
            ),
            ScenarioStep(
                step_number=6,
                description="Enable and start Samba services:\n"
                           "  - smb service\n"
                           "  - nmb service",
                task_type="multi_service_enable",
                task_params={'services': ['smb', 'nmb']},
                points=4,
                hints=[
                    "systemctl enable --now smb nmb",
                ],
                depends_on=[4, 5],
            ),
        ],
    )


@ScenarioRegistry.register("secure_admin_setup")
def create_secure_admin_scenario() -> Scenario:
    """Create a secure admin account scenario."""
    admin_user = f"secadmin{random.randint(1, 99)}"

    return Scenario(
        id="secure_admin_setup",
        title="Secure Administrator Setup",
        description="Create a secure administrator account with proper sudo access and SSH configuration.",
        difficulty="hard",
        category="security",
        total_points=28,
        time_estimate_minutes=15,
        context="A new system administrator is joining the team. Create their account "
                "with appropriate privileges following security best practices.",
        objectives=[
            "Create admin user account",
            "Configure secure sudo access",
            "Set up SSH key authentication",
            "Configure password policies",
        ],
        steps=[
            ScenarioStep(
                step_number=1,
                description=f"Create the administrator account:\n"
                           f"  - Username: {admin_user}\n"
                           f"  - UID: 1500\n"
                           f"  - Groups: wheel, sysadmin\n"
                           f"  - Home: /home/{admin_user}",
                task_type="user_create",
                task_params={'username': admin_user, 'uid': 1500, 'groups': ['wheel', 'sysadmin']},
                points=8,
                hints=[
                    "May need to create sysadmin group first",
                    "useradd -u 1500 -G wheel,sysadmin -m username",
                ],
            ),
            ScenarioStep(
                step_number=2,
                description=f"Configure sudo for {admin_user}:\n"
                           f"  - Allow ALL commands\n"
                           f"  - Require password\n"
                           f"  - Log all sudo commands",
                task_type="sudo_config",
                task_params={'username': admin_user, 'nopasswd': False},
                points=6,
                hints=[
                    f"Create /etc/sudoers.d/{admin_user}",
                    f"{admin_user} ALL=(ALL) ALL",
                    "Defaults:{admin_user} logfile=/var/log/sudo_{admin_user}.log",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=3,
                description=f"Create .ssh directory for {admin_user}:\n"
                           f"  - Path: /home/{admin_user}/.ssh\n"
                           f"  - Permissions: 700\n"
                           f"  - Owner: {admin_user}",
                task_type="directory_setup",
                task_params={'path': f'/home/{admin_user}/.ssh', 'mode': '700', 'owner': admin_user},
                points=4,
                hints=[
                    "mkdir /home/user/.ssh",
                    "chmod 700 /home/user/.ssh",
                    "chown user:user /home/user/.ssh",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=4,
                description=f"Set password aging for {admin_user}:\n"
                           f"  - Maximum days: 90\n"
                           f"  - Minimum days: 7\n"
                           f"  - Warning days: 14",
                task_type="password_policy",
                task_params={'username': admin_user, 'max_days': 90, 'min_days': 7, 'warn_days': 14},
                points=6,
                hints=[
                    "chage -M 90 -m 7 -W 14 username",
                    "Verify with chage -l username",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=5,
                description=f"Lock the root account from direct login:\n"
                           f"  - Disable root password login\n"
                           f"  - Keep root accessible via sudo",
                task_type="account_security",
                task_params={'action': 'lock_root'},
                points=4,
                hints=[
                    "passwd -l root (locks password)",
                    "Or edit /etc/ssh/sshd_config: PermitRootLogin no",
                ],
            ),
        ],
    )


@ScenarioRegistry.register("container_app_deploy")
def create_container_deployment_scenario() -> Scenario:
    """Create a container application deployment scenario."""
    app_name = f"webapp{random.randint(1, 99)}"

    return Scenario(
        id="container_app_deploy",
        title="Container Application Deployment",
        description="Deploy a containerized web application using Podman with persistent storage.",
        difficulty="hard",
        category="containers",
        total_points=30,
        time_estimate_minutes=20,
        context="Deploy a containerized web application that needs persistent storage "
                "and must run as a non-root user with systemd integration.",
        objectives=[
            "Create application user",
            "Set up persistent storage",
            "Configure container to run rootless",
            "Create systemd service for container",
        ],
        steps=[
            ScenarioStep(
                step_number=1,
                description=f"Create user for running containers:\n"
                           f"  - Username: {app_name}\n"
                           f"  - UID: 4000\n"
                           f"  - Enable lingering for user services",
                task_type="container_user",
                task_params={'username': app_name, 'uid': 4000},
                points=6,
                hints=[
                    f"useradd -u 4000 {app_name}",
                    f"loginctl enable-linger {app_name}",
                ],
            ),
            ScenarioStep(
                step_number=2,
                description=f"Create persistent storage directory:\n"
                           f"  - Path: /srv/containers/{app_name}/data\n"
                           f"  - Owner: {app_name} (UID 4000)\n"
                           f"  - SELinux: container_file_t",
                task_type="container_storage",
                task_params={'path': f'/srv/containers/{app_name}/data', 'uid': 4000},
                points=8,
                hints=[
                    "mkdir -p /srv/containers/app/data",
                    "chown -R 4000:4000 /srv/containers/app",
                    "semanage fcontext -a -t container_file_t '/srv/containers/app(/.*)?'",
                    "restorecon -Rv /srv/containers/app",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=3,
                description=f"Pull and run container as {app_name}:\n"
                           f"  - Image: registry.access.redhat.com/ubi8/httpd-24\n"
                           f"  - Name: {app_name}-httpd\n"
                           f"  - Port: 8080:8080\n"
                           f"  - Volume: /srv/containers/{app_name}/data:/var/www/html:Z",
                task_type="container_run",
                task_params={
                    'image': 'registry.access.redhat.com/ubi8/httpd-24',
                    'name': f'{app_name}-httpd',
                    'port': '8080:8080',
                    'volume': f'/srv/containers/{app_name}/data:/var/www/html:Z',
                    'user': app_name,
                },
                points=8,
                hints=[
                    f"su - {app_name}",
                    f"podman run -d --name {app_name}-httpd -p 8080:8080 -v /path:/var/www/html:Z image",
                ],
                depends_on=[2],
            ),
            ScenarioStep(
                step_number=4,
                description=f"Generate and enable systemd service:\n"
                           f"  - Generate user service file\n"
                           f"  - Enable service to start on boot",
                task_type="container_systemd",
                task_params={'container_name': f'{app_name}-httpd', 'user': app_name},
                points=8,
                hints=[
                    f"podman generate systemd --name {app_name}-httpd --files --new",
                    "mkdir -p ~/.config/systemd/user",
                    "mv container-*.service ~/.config/systemd/user/",
                    "systemctl --user daemon-reload",
                    "systemctl --user enable container-{app_name}-httpd.service",
                ],
                depends_on=[3],
            ),
        ],
    )


@ScenarioRegistry.register("storage_lvm_setup")
def create_lvm_storage_scenario() -> Scenario:
    """Create an LVM storage setup scenario."""
    vg_name = f"datavg{random.randint(1, 9)}"
    lv_name = f"datalv{random.randint(1, 9)}"

    return Scenario(
        id="storage_lvm_setup",
        title="LVM Storage Configuration",
        description="Configure LVM storage with a volume group, logical volume, and persistent mount.",
        difficulty="exam",
        category="storage",
        total_points=35,
        time_estimate_minutes=25,
        context="Add new storage capacity using LVM to allow for flexible resizing. "
                "The storage will be used for application data.",
        objectives=[
            "Create physical volumes",
            "Create volume group",
            "Create logical volume",
            "Format and mount filesystem",
            "Configure persistent mount",
        ],
        steps=[
            ScenarioStep(
                step_number=1,
                description="Create physical volume:\n"
                           "  - Device: /dev/sdb (or available disk)\n"
                           "  - Initialize for LVM use",
                task_type="lvm_pv",
                task_params={'device': '/dev/sdb'},
                points=5,
                hints=[
                    "pvcreate /dev/sdb",
                    "Verify with pvs or pvdisplay",
                ],
            ),
            ScenarioStep(
                step_number=2,
                description=f"Create volume group:\n"
                           f"  - Name: {vg_name}\n"
                           f"  - Physical volume: /dev/sdb",
                task_type="lvm_vg",
                task_params={'vg_name': vg_name, 'pv': '/dev/sdb'},
                points=6,
                hints=[
                    f"vgcreate {vg_name} /dev/sdb",
                    "Verify with vgs or vgdisplay",
                ],
                depends_on=[1],
            ),
            ScenarioStep(
                step_number=3,
                description=f"Create logical volume:\n"
                           f"  - Name: {lv_name}\n"
                           f"  - Volume group: {vg_name}\n"
                           f"  - Size: 500M",
                task_type="lvm_lv",
                task_params={'lv_name': lv_name, 'vg_name': vg_name, 'size': '500M'},
                points=6,
                hints=[
                    f"lvcreate -L 500M -n {lv_name} {vg_name}",
                    "Verify with lvs or lvdisplay",
                ],
                depends_on=[2],
            ),
            ScenarioStep(
                step_number=4,
                description=f"Create XFS filesystem:\n"
                           f"  - Device: /dev/{vg_name}/{lv_name}\n"
                           f"  - Filesystem: XFS",
                task_type="filesystem_create",
                task_params={'device': f'/dev/{vg_name}/{lv_name}', 'fstype': 'xfs'},
                points=5,
                hints=[
                    f"mkfs.xfs /dev/{vg_name}/{lv_name}",
                ],
                depends_on=[3],
            ),
            ScenarioStep(
                step_number=5,
                description=f"Create mount point and mount:\n"
                           f"  - Mount point: /mnt/data\n"
                           f"  - Verify mount works",
                task_type="mount_filesystem",
                task_params={'device': f'/dev/{vg_name}/{lv_name}', 'mountpoint': '/mnt/data'},
                points=5,
                hints=[
                    "mkdir -p /mnt/data",
                    f"mount /dev/{vg_name}/{lv_name} /mnt/data",
                ],
                depends_on=[4],
            ),
            ScenarioStep(
                step_number=6,
                description="Configure persistent mount in /etc/fstab:\n"
                           "  - Use device path or UUID\n"
                           "  - Filesystem: xfs\n"
                           "  - Options: defaults",
                task_type="fstab_entry",
                task_params={'device': f'/dev/{vg_name}/{lv_name}', 'mountpoint': '/mnt/data', 'fstype': 'xfs'},
                points=8,
                hints=[
                    f"/dev/{vg_name}/{lv_name} /mnt/data xfs defaults 0 0",
                    "Or use UUID from blkid",
                    "Test with: umount /mnt/data && mount -a",
                ],
                depends_on=[5],
            ),
        ],
    )


class ScenarioSession:
    """Manages an active scenario session."""

    def __init__(self, scenario: Scenario):
        """Initialize scenario session."""
        self.scenario = scenario
        self.current_step = 1
        self.completed_steps: List[int] = []
        self.step_results: Dict[int, ValidationResult] = {}
        self.start_time = None
        self.end_time = None

    def get_current_step(self) -> Optional[ScenarioStep]:
        """Get the current step."""
        return self.scenario.get_step(self.current_step)

    def can_attempt_step(self, step_number: int) -> bool:
        """Check if a step can be attempted (dependencies met)."""
        step = self.scenario.get_step(step_number)
        if not step:
            return False

        # Check if all dependencies are completed
        for dep in step.depends_on:
            if dep not in self.completed_steps:
                return False
        return True

    def complete_step(self, step_number: int, result: ValidationResult):
        """Mark a step as completed."""
        self.step_results[step_number] = result
        if result.passed:
            self.completed_steps.append(step_number)
            # Auto-advance to next incomplete step
            self._advance_to_next_step()

    def _advance_to_next_step(self):
        """Advance to next available step."""
        for step in self.scenario.steps:
            if step.step_number not in self.completed_steps:
                if self.can_attempt_step(step.step_number):
                    self.current_step = step.step_number
                    return
        # All steps completed
        self.current_step = -1

    def is_complete(self) -> bool:
        """Check if scenario is complete."""
        return len(self.completed_steps) == len(self.scenario.steps)

    def get_progress(self) -> Dict:
        """Get scenario progress."""
        total_points = sum(s.points for s in self.scenario.steps)
        earned_points = sum(
            self.step_results[s].score
            for s in self.completed_steps
            if s in self.step_results
        )

        return {
            'total_steps': len(self.scenario.steps),
            'completed_steps': len(self.completed_steps),
            'current_step': self.current_step,
            'total_points': total_points,
            'earned_points': earned_points,
            'percentage': (earned_points / total_points * 100) if total_points > 0 else 0,
        }
