# RHCSA Mock Exam Simulator

A realistic command-line RHCSA (Red Hat Certified System Administrator) exam simulator that generates exam tasks, validates your system configuration, and tracks your progress over time.

## Features

- **Full Exam Mode**: Simulates a complete RHCSA exam with 15-20 tasks covering all objectives
- **Practice Mode**: Focus on specific categories (Users, LVM, SELinux, etc.) at different difficulty levels
- **Automatic Validation**: Validates your system configuration using safe, read-only commands
- **Progress Tracking**: Saves exam results and displays statistics over time
- **Timer Support**: Optional 2.5-hour timer to simulate real exam conditions
- **Detailed Feedback**: Shows exactly what was checked and why tasks pass or fail
- **Offline Operation**: No internet connection required
- **Safe & Secure**: Uses command whitelisting and validation-only approach

## Requirements

- **OS**: RHEL 8/9, Rocky Linux 8/9, or Alma Linux 8/9
- **Python**: 3.6 or later (included in RHEL 8/9)
- **Privileges**: Must run as root (uses `sudo`)
- **Dependencies**: None (uses Python standard library only)

## Installation

### Quick Install

```bash
# Download or clone the repository
cd rhcsa-simulator

# Run installation script
sudo ./install.sh
```

The installer will:
- Check Python version
- Copy files to `/opt/rhcsa-simulator`
- Create symlink at `/usr/local/bin/rhcsa-simulator`
- Set proper permissions

### Manual Installation

```bash
sudo mkdir -p /opt/rhcsa-simulator
sudo cp -r * /opt/rhcsa-simulator/
sudo chmod +x /opt/rhcsa-simulator/rhcsa_simulator.py
sudo ln -s /opt/rhcsa-simulator/rhcsa_simulator.py /usr/local/bin/rhcsa-simulator
```

## Usage

### Launch the Simulator

```bash
sudo rhcsa-simulator
```

**Note**: Root privileges are required to validate system state (users, services, permissions, etc.)

### Exam Mode

1. Select "Exam Mode" from main menu
2. Review exam information (tasks, duration, pass threshold)
3. Press Enter to generate exam tasks
4. Read all tasks carefully
5. Complete tasks on your Linux system
6. Return to simulator and press Enter to validate
7. Review your results and detailed feedback

### Practice Mode

1. Select "Practice Mode" from main menu
2. Choose a category:
   - Users & Groups
   - Permissions & ACLs
   - LVM (Logical Volume Management)
   - SELinux
   - Services (systemd)
   - And more...
3. Select difficulty level (easy/exam/hard)
4. Complete each task and get immediate feedback

### View Progress

Track your improvement over time:
- Overall statistics (average score, pass rate)
- Recent exam results
- Performance by category

## Task Categories

The simulator covers all RHCSA exam objectives:

1. **Essential Tools** - find, grep, tar, archives
2. **Users & Groups** - user/group management, sudo
3. **Permissions** - chmod, chown, ACLs, special bits
4. **LVM** - physical volumes, volume groups, logical volumes
5. **File Systems** - create, mount, fstab, XFS, ext4
6. **Networking** - interface configuration, DNS, hostnames
7. **SELinux** - contexts, booleans, modes
8. **Services** - systemd service management
9. **Boot Targets** - multi-user, graphical targets
10. **Processes** - process management, priorities
11. **Scheduling** - cron, at, systemd timers
12. **Containers** - Podman basics

## Example Tasks

### User Management
```
Task: Create a user named 'examuser42' with the following requirements:
  - UID: 2500
  - Primary group: developers
  - Supplementary groups: wheel, sysadmin
  - Home directory: /home/examuser42
  - Login shell: /bin/bash
```

### SELinux
```
Task: Configure SELinux context for directory '/srv/web01':
  - Set SELinux type to: httpd_sys_content_t
  - Apply context recursively to all files
  - Make the change persistent across relabels
```

### Services
```
Task: Configure the 'httpd' service:
  - Start the service
  - Enable the service to start at boot
```

## How It Works

### Validation Process

The simulator uses **read-only validation**:
- Does NOT modify your system
- Only checks if tasks were completed correctly
- Uses safe, whitelisted commands (`id`, `ls`, `systemctl status`, etc.)
- All commands have timeout protection
- Command injection prevention

### Scoring

- Each task has a point value (4-12 points typically)
- Tasks have multiple validation checks
- Partial credit is awarded for partial completion
- Pass threshold: 70% (configurable)

### Results Storage

Results are saved to JSON files in `/opt/rhcsa-simulator/data/results/`:
- Exam ID and timestamp
- Task-by-task results
- Category breakdown
- Total score and pass/fail status

## Architecture

```
rhcsa-simulator/
├── rhcsa_simulator.py       # Main entry point
├── config/                   # Configuration
├── core/                     # Orchestration (exam, practice, menu, results)
├── tasks/                    # Task categories (20+ task types)
├── validators/               # Validation framework
├── utils/                    # Utilities (logging, formatting, helpers)
└── data/                     # Results storage
```

## Extending the Simulator

### Adding New Tasks

1. Open the appropriate category file (e.g., `tasks/users_groups.py`)
2. Create a new class extending `BaseTask`
3. Register with `@TaskRegistry.register("category_name")`
4. Implement `generate()` and `validate()` methods

Example:

```python
@TaskRegistry.register("users_groups")
class MyNewTask(BaseTask):
    def __init__(self):
        super().__init__(
            id="my_task_001",
            category="users_groups",
            difficulty="exam",
            points=8
        )

    def generate(self, **params):
        self.description = "Task description here"
        self.hints = ["Hint 1", "Hint 2"]
        return self

    def validate(self):
        checks = []
        # Add validation checks
        return ValidationResult(self.id, passed, score, max_score, checks)
```

## Security

- **Command Whitelisting**: Only approved read-only commands
- **Timeout Protection**: All commands have 5-second timeout
- **Pattern Blocking**: Detects dangerous patterns (rm -rf, etc.)
- **No System Modifications**: Validation is read-only
- **Root Required**: Needed to check system state, not to modify it

## Troubleshooting

### "Must run as root" error
```bash
sudo rhcsa-simulator  # Don't forget sudo!
```

### Module import errors
```bash
# Ensure you're in the correct directory
cd /opt/rhcsa-simulator
sudo python3 rhcsa_simulator.py
```

### No tasks available
- Run `sudo rhcsa-simulator` to initialize task registry
- Check logs at `/opt/rhcsa-simulator/data/logs/rhcsa_simulator.log`

## Development

### Project Stats
- **Lines of Code**: ~5,500
- **Task Categories**: 12
- **Task Types**: 20+ implemented, expandable to 100+
- **Validators**: 50+ validation functions
- **Dependencies**: 0 (Python stdlib only)

### Testing Tasks

```python
# Run from project root
cd /opt/rhcsa-simulator
sudo python3 -c "
from tasks.registry import TaskRegistry
TaskRegistry.initialize()
TaskRegistry.print_statistics()
"
```

## Contributing

To add more tasks:
1. Choose a category or create a new one
2. Follow the pattern in `tasks/users_groups.py`
3. Use existing validators from `validators/` modules
4. Test thoroughly on a test system

## License

This is an educational tool for RHCSA exam preparation. Use at your own risk on test systems only.

## Disclaimer

- This simulator is NOT affiliated with Red Hat
- Practice on test systems only
- Always backup important data
- Validation commands are safe but require root to check system state

## Resources

- [RHCSA Exam Objectives](https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam)
- [RHEL Documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/)

## Version

**v1.0.0** - Initial release

---

**Good luck with your RHCSA certification!** 🎓
