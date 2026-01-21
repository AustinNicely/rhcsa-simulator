# RHCSA Mock Exam Simulator

A realistic command-line RHCSA (Red Hat Certified System Administrator) exam simulator that generates exam tasks, validates your system configuration, and tracks your progress over time.

## Features

### Learning Modes
- **Learn Mode**: Study RHCSA concepts with detailed explanations, command syntax, examples, common mistakes, and exam tricks
- **Guided Practice**: Practice tasks with progressive 3-level hints (concept → command structure → full solution)
- **Command Recall Training**: Build muscle memory by typing commands before execution with instant accuracy feedback

### Testing Modes
- **Full Exam Mode**: Simulates a complete RHCSA exam with 15-20 tasks covering all objectives
- **Practice Mode**: Focus on specific categories (Users, LVM, SELinux, etc.) at different difficulty levels with **retry support**
- **Scenario Mode**: Multi-step real-world scenarios that combine multiple skills
- **Troubleshooting Mode**: Diagnose and fix broken system configurations

### Core Features
- **Automatic Validation**: Validates your system configuration using safe, read-only commands
- **Adaptive Feedback**: Explains what was expected vs. what was found for each failed check
- **Progress Tracking**: Saves exam results and displays statistics over time
- **Weak Area Analysis**: Identifies your weak spots and provides targeted recommendations
- **Bookmarks**: Save difficult tasks to revisit later
- **Export Reports**: Generate progress reports in TXT, HTML, or PDF format
- **Timer Support**: Optional 2.5-hour timer to simulate real exam conditions
- **Offline Operation**: No internet connection required
- **Safe & Secure**: Uses command whitelisting and validation-only approach

### Practice Disk Support
- **Dynamic Device Detection**: LVM tasks automatically detect available disks
- **Loop Device Support**: Create virtual practice disks - no extra hardware needed!
- **Easy Setup**: Menu-driven setup for practice disks (option 13)
- **Works on Cloud VMs**: Practice LVM on AWS/Azure/GCP without adding volumes

### AI-Powered Feedback (Optional)
- **Intelligent Analysis**: Line-by-line command analysis using Claude AI
- **Smart Explanations**: Understands WHY you failed, not just that you failed
- **Approach Comparison**: Compares your solution to optimal approaches
- **Contextual Tips**: RHCSA exam tips personalized to each task
- **Command Tracking**: Automatically tracks and categorizes commands you execute

**Setup**: See [AI_SETUP.md](AI_SETUP.md) for configuration instructions (requires Anthropic API key)

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

### Learn Mode

1. Select "Learn Mode" from main menu
2. Choose a topic to study
3. Review:
   - Concept explanations
   - Command syntax with examples
   - Common mistakes to avoid
   - Exam-specific tricks and tips
4. Optionally jump to practice mode for that topic

### Guided Practice Mode

1. Select "Guided Practice" from main menu
2. Choose a category and difficulty level
3. Read each task carefully
4. Use progressive hints if needed:
   - Hint 1: Concept reminder
   - Hint 2: Command structure and syntax
   - Hint 3: Full solution with examples
5. Complete task and get adaptive feedback
6. Review detailed explanations for any failures

### Command Recall Training

1. Select "Command Recall" from main menu
2. Choose a category and difficulty level
3. Read the task description
4. Type the command(s) you would use
5. Get instant feedback on command accuracy
6. Build muscle memory and improve speed

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
5. **If you fail**: Choose to Retry, see Solution, or Continue
6. Review fix suggestions for each failed check

### Setup Practice Disks (for LVM)

If you don't have spare disks for LVM practice:

1. Select "Setup Practice Disks" from main menu (option 13)
2. Choose "Create practice disks (2 x 500MB)"
3. Virtual loop devices are created automatically
4. LVM tasks will now use these devices

**Manual method:**
```bash
# Create disk images
sudo dd if=/dev/zero of=/tmp/disk1.img bs=1M count=500
sudo dd if=/dev/zero of=/tmp/disk2.img bs=1M count=500

# Attach as loop devices
sudo losetup -f --show /tmp/disk1.img  # Returns /dev/loop0
sudo losetup -f --show /tmp/disk2.img  # Returns /dev/loop1

# Now practice LVM on /dev/loop0, /dev/loop1
```

### View Progress

Track your improvement over time:
- Overall statistics (average score, pass rate)
- Recent exam results
- Performance by category

### Weak Area Analysis

Identify where you need more practice:
1. Select "Weak Areas" from main menu
2. View categories with lowest success rates
3. Get personalized recommendations
4. Focus your study time effectively

### Bookmarks

Save tasks to revisit later:
- Bookmark difficult tasks during practice
- Review all bookmarked tasks from menu
- Clear bookmarks when mastered

### Export Reports

Generate progress reports:
1. Select "Export Report" from main menu
2. Choose format: TXT, HTML, or PDF
3. Share or print your progress

## Recommended Learning Path

For best results, follow this progression:

1. **Learn** - Study each topic with Learn Mode
   - Understand concepts before practicing
   - Review command syntax and examples
   - Learn common mistakes and exam tricks

2. **Guided Practice** - Build confidence with hints
   - Start practicing tasks with support
   - Use hints when stuck
   - Learn from adaptive feedback

3. **Command Recall** - Build muscle memory
   - Practice typing commands from memory
   - Improve speed and accuracy
   - Build exam-day confidence

4. **Practice Mode** - Test without hints
   - Validate your knowledge independently
   - Identify weak areas
   - Build problem-solving skills

5. **Exam Mode** - Full exam simulation
   - Take complete timed exams
   - Simulate real exam pressure
   - Track your progress over time

**Pro Tip**: Cycle through topics rather than mastering one at a time. This improves retention and helps you see connections between different RHCSA objectives.

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

### LVM tasks reference missing devices (e.g., /dev/vdb)
Use the built-in practice disk feature:
```bash
sudo rhcsa-simulator
# Select option 13: Setup Practice Disks
# Create 2 x 500MB practice disks
```

Or manually:
```bash
sudo dd if=/dev/zero of=/tmp/disk1.img bs=1M count=500
sudo losetup -f --show /tmp/disk1.img
# Use the returned device (e.g., /dev/loop0) for LVM practice
```

### Cleaning up practice disks
```bash
# Remove LVM structures first
sudo vgremove -f <vgname>
sudo pvremove /dev/loop0

# Detach loop devices
sudo losetup -d /dev/loop0
sudo losetup -d /dev/loop1

# Remove image files
sudo rm /var/lib/rhcsa-simulator/loops/*.img
```

## Development

### Project Stats
- **Lines of Code**: ~7,000+
- **Task Categories**: 12
- **Task Types**: 25+ implemented, expandable to 100+
- **Validators**: 50+ validation functions
- **Modes**: 7 (Learn, Guided Practice, Command Recall, Exam, Practice, Scenario, Troubleshoot)
- **Dependencies**: 0 (Python stdlib only, optional: anthropic for AI feedback)

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

**v2.2.0** - Practice Disk Support
- Dynamic device detection for LVM tasks
- Loop device support - practice LVM without extra disks
- "Setup Practice Disks" menu option
- Works on cloud VMs (AWS, Azure, GCP) without adding volumes

**v2.1.0** - Enhanced Practice & Analytics
- Retry option in Practice Mode (R to retry, S for solution)
- Scenario Mode - multi-step real-world scenarios
- Troubleshooting Mode - diagnose broken systems
- Weak Area Analysis with recommendations
- Bookmarks - save tasks for later
- Export Reports (TXT, HTML, PDF)
- Fix suggestions for failed validation checks

**v2.0.0** - AI-Powered Feedback Release
- Added AI-powered intelligent feedback using Claude API
- Command history tracking and analysis
- Line-by-line approach comparison
- Contextual failure explanations
- Complete RHCSA exam coverage (all 12 categories)

**v1.0.0** - Initial release

---

**Good luck with your RHCSA certification!**
