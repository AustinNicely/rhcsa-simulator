# RHCSA Simulator Development Notes

## Session Summary (January 2026)

### Bug Fix: ValidationCheck max_points
**Problem:** Failed validation checks showed "(0/0 points)" instead of "(0/3 points)"

**Solution:** Added `max_points` field to `ValidationCheck` class in `core/validator.py`:
```python
@dataclass
class ValidationCheck:
    name: str
    passed: bool
    points: int
    message: str
    max_points: Optional[int] = None
    details: Optional[str] = None

    def __post_init__(self):
        if self.max_points is None:
            self.max_points = self.points
```

Updated all task files to include `max_points` for failed checks.

---

### New Features Implemented

#### 1. Explanations Engine (`core/explanations.py`)
- Explains why checks pass/fail
- Command explanations with syntax help
- Task-specific guidance

#### 2. Mistakes Tracker (`core/mistakes_tracker.py`)
- Records common mistakes
- Tracks weak categories
- Generates recommendations

#### 3. Scenario Mode (`core/scenarios.py`, `core/scenario_mode.py`)
5 multi-step scenarios:
- web_server_setup
- samba_share_setup
- secure_admin_setup
- container_app_deploy
- storage_lvm_setup

#### 4. Troubleshooting Mode (`core/troubleshoot_mode.py`, `tasks/troubleshooting.py`)
5 troubleshooting tasks:
- SSHNotStartingTask
- WebServerNotWorkingTask
- UserCannotLoginTask
- FilesystemNotMountingTask
- SudoNotWorkingTask

#### 5. Enhanced Timer (`core/timer.py`)
- Configurable warning thresholds (60/30/15/10/5/2/1 minutes)
- Colored output for urgency

#### 6. Bookmarks & Weak Area Analysis (`core/bookmarks.py`)
- Save tasks for later review
- Track performance by category
- Generate study recommendations

#### 7. Export Reports (`core/export.py`)
- Text, HTML, PDF formats
- Progress reports
- Exam result reports

#### 8. Task Reset (`core/reset.py`)
- Reset task state
- Clean up test artifacts

#### 9. RHCSA 9 Storage Tasks (`tasks/storage_advanced.py`)
- Stratis pool/filesystem/snapshot
- LVM thin pools
- Swap file/partition configuration

---

### Menu Options (13 total)
1. Learn Mode
2. Guided Practice
3. Command Recall
4. Exam Mode
5. Practice Mode
6. Scenario Mode [NEW]
7. Troubleshooting [NEW]
8. View Progress
9. Weak Areas [NEW]
10. Bookmarks [NEW]
11. Export Report [NEW]
12. Task Statistics
13. Help
0. Exit

---

### Files Modified/Created

**New Files:**
- `core/explanations.py`
- `core/mistakes_tracker.py`
- `core/scenarios.py`
- `core/scenario_mode.py`
- `core/timer.py`
- `core/bookmarks.py`
- `core/export.py`
- `core/reset.py`
- `core/troubleshoot_mode.py`
- `tasks/troubleshooting.py`
- `tasks/storage_advanced.py`

**Modified Files:**
- `core/validator.py` - Added max_points field
- `core/menu.py` - Updated with 13 options
- `core/practice.py` - Updated display code
- `core/exam.py` - Updated display code
- `utils/formatters.py` - Added new display functions
- `rhcsa_simulator.py` - Added new mode handlers
- All task files - Added max_points to failed checks

---

### Quick Reference Commands

**SELinux Booleans:**
```bash
# Persistent
sudo setsebool -P httpd_enable_homedirs on

# Check
getsebool httpd_enable_homedirs
```

**Run Simulator:**
```bash
cd rhcsa-simulator
sudo python3 rhcsa_simulator.py
```

**Clone from GitHub:**
```bash
git clone https://github.com/AustinNicely/rhcsa-simulator.git
```

---

### Potential Future Improvements
- Add more scenarios (NFS, iSCSI, LDAP authentication)
- Implement actual task reset functionality
- Add difficulty progression system
- Create practice exam templates
- Add network troubleshooting tasks
- Implement timed practice sessions
- Add flashcard mode for commands
