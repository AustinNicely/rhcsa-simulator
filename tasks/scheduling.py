"""
Task scheduling tasks for RHCSA exam (cron, at, systemd timers).
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.system_validators import get_user_crontab, validate_cron_entry
from validators.safe_executor import execute_safe


logger = logging.getLogger(__name__)


@TaskRegistry.register("scheduling")
class CreateCronJobTask(BaseTask):
    """Create a user cron job."""

    def __init__(self):
        super().__init__(
            id="sched_cron_001",
            category="scheduling",
            difficulty="medium",
            points=10
        )
        self.username = None
        self.command = None
        self.schedule = None
        self.schedule_desc = None

    def generate(self, **params):
        """Generate cron job task."""
        self.username = params.get('username', 'root')

        schedules = [
            ('0 2 * * *', 'daily at 2:00 AM'),
            ('*/15 * * * *', 'every 15 minutes'),
            ('0 */6 * * *', 'every 6 hours'),
            ('0 0 * * 0', 'weekly on Sunday at midnight'),
            ('30 1 * * 1-5', 'weekdays at 1:30 AM'),
        ]

        commands = [
            '/usr/bin/backup.sh',
            '/usr/local/bin/cleanup.sh',
            'echo "Scheduled task" >> /tmp/cronlog.txt',
        ]

        if params.get('schedule'):
            self.schedule = params['schedule']
            self.schedule_desc = params.get('schedule_desc', self.schedule)
        else:
            self.schedule, self.schedule_desc = random.choice(schedules)

        self.command = params.get('command', random.choice(commands))

        self.description = (
            f"Create a cron job:\n"
            f"  - User: {self.username}\n"
            f"  - Schedule: {self.schedule_desc}\n"
            f"  - Cron expression: {self.schedule}\n"
            f"  - Command: {self.command}\n"
            f"  - Use crontab command to configure"
        )

        self.hints = [
            f"Edit crontab: crontab -e (for current user) or crontab -e -u {self.username}",
            f"Add line: {self.schedule} {self.command}",
            "Cron format: minute hour day month weekday command",
            f"Verify: crontab -l -u {self.username}",
            "* means 'every'",
            "*/15 means 'every 15th'"
        ]

        return self

    def validate(self):
        """Validate cron job exists."""
        checks = []
        total_points = 0

        # Check if crontab entry exists
        entries = get_user_crontab(self.username)

        if entries is not None:
            # Look for the command in crontab
            found = False
            for entry in entries:
                if self.command in entry:
                    # Also check if schedule matches
                    if self.schedule in entry:
                        found = True
                        checks.append(ValidationCheck(
                            name="cron_entry_exact",
                            passed=True,
                            points=10,
                            message=f"Cron job correctly configured with exact schedule"
                        ))
                        total_points += 10
                        break
                    else:
                        # Command found but schedule might be different
                        checks.append(ValidationCheck(
                            name="cron_entry_partial",
                            passed=True,
                            points=5,
                            message=f"Command found in crontab but schedule may differ (partial credit)"
                        ))
                        total_points += 5
                        found = True
                        break

            if not found:
                checks.append(ValidationCheck(
                    name="cron_entry",
                    passed=False,
                    points=0,
                    max_points=10,
                    message=f"Cron job not found in crontab for user {self.username}"
                ))
        else:
            checks.append(ValidationCheck(
                name="crontab_exists",
                passed=False,
                points=0,
                max_points=10,
                message=f"No crontab found for user {self.username}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("scheduling")
class CreateSystemCronTask(BaseTask):
    """Create a system-wide cron job in /etc/cron.d/."""

    def __init__(self):
        super().__init__(
            id="sched_system_cron_001",
            category="scheduling",
            difficulty="medium",
            points=12
        )
        self.job_name = None
        self.command = None
        self.schedule = None
        self.user = None

    def generate(self, **params):
        """Generate system cron task."""
        self.job_name = params.get('job_name', f'custom-job-{random.randint(1,99)}')
        self.user = params.get('user', 'root')
        self.schedule = params.get('schedule', '0 3 * * *')
        self.command = params.get('command', '/usr/local/bin/maintenance.sh')

        self.description = (
            f"Create a system-wide cron job:\n"
            f"  - Job name: {self.job_name}\n"
            f"  - File: /etc/cron.d/{self.job_name}\n"
            f"  - Run as user: {self.user}\n"
            f"  - Schedule: {self.schedule}\n"
            f"  - Command: {self.command}\n"
            f"  - Configure in /etc/cron.d/ (not user crontab)"
        )

        self.hints = [
            f"Create file: /etc/cron.d/{self.job_name}",
            f"Format: {self.schedule} {self.user} {self.command}",
            "System cron format: min hour day month weekday user command",
            "Permissions: chmod 644 /etc/cron.d/{job_name}",
            "No need to restart cron service"
        ]

        return self

    def validate(self):
        """Validate system cron job."""
        checks = []
        total_points = 0

        import os
        from validators.file_validators import validate_file_contains

        cron_file = f'/etc/cron.d/{self.job_name}'

        # Check 1: File exists (4 points)
        if os.path.exists(cron_file):
            checks.append(ValidationCheck(
                name="file_exists",
                passed=True,
                points=4,
                message=f"Cron file exists at {cron_file}"
            ))
            total_points += 4

            # Check 2: Contains command (4 points)
            if validate_file_contains(cron_file, self.command):
                checks.append(ValidationCheck(
                    name="command_present",
                    passed=True,
                    points=4,
                    message=f"Command found in cron file"
                ))
                total_points += 4
            else:
                checks.append(ValidationCheck(
                    name="command_present",
                    passed=False,
                    points=0,
                    max_points=4,
                    message=f"Command not found in {cron_file}"
                ))

            # Check 3: Contains user (2 points)
            if validate_file_contains(cron_file, self.user):
                checks.append(ValidationCheck(
                    name="user_specified",
                    passed=True,
                    points=2,
                    message=f"User '{self.user}' specified in cron file"
                ))
                total_points += 2
            else:
                checks.append(ValidationCheck(
                    name="user_specified",
                    passed=False,
                    points=0,
                    max_points=2,
                    message=f"User not found in {cron_file}"
                ))

            # Check 4: Contains schedule (2 points)
            if validate_file_contains(cron_file, self.schedule):
                checks.append(ValidationCheck(
                    name="schedule_correct",
                    passed=True,
                    points=2,
                    message=f"Schedule configured correctly"
                ))
                total_points += 2
            else:
                checks.append(ValidationCheck(
                    name="schedule_correct",
                    passed=False,
                    points=0,
                    max_points=2,
                    message=f"Schedule not found in {cron_file}"
                ))
        else:
            checks.append(ValidationCheck(
                name="file_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Cron file {cron_file} not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("scheduling")
class CreateAtJobTask(BaseTask):
    """Schedule a one-time task with at command."""

    def __init__(self):
        super().__init__(
            id="sched_at_001",
            category="scheduling",
            difficulty="easy",
            points=8
        )
        self.time_spec = None
        self.command = None

    def generate(self, **params):
        """Generate at job task."""
        time_specs = [
            ('now + 1 hour', 'in 1 hour'),
            ('now + 30 minutes', 'in 30 minutes'),
            ('tomorrow', 'tomorrow at current time'),
            ('16:00', 'today at 4:00 PM'),
        ]

        if params.get('time'):
            self.time_spec = params['time']
            time_desc = params.get('time_desc', self.time_spec)
        else:
            self.time_spec, time_desc = random.choice(time_specs)

        self.command = params.get('command', 'echo "At job executed" >> /tmp/atjob.log')

        self.description = (
            f"Schedule a one-time task:\n"
            f"  - Time: {time_desc}\n"
            f"  - At spec: {self.time_spec}\n"
            f"  - Command: {self.command}\n"
            f"  - Use the 'at' command"
        )

        self.hints = [
            f"Schedule with at: echo '{self.command}' | at {self.time_spec}",
            "Or use: at {time} <<< '{command}'",
            "View scheduled jobs: atq",
            "View job details: at -c <job_number>",
            "Remove job: atrm <job_number>",
            "Ensure atd service is running: systemctl status atd"
        ]

        return self

    def validate(self):
        """Validate at job is scheduled."""
        checks = []
        total_points = 0

        # Check if atd service is running (3 points)
        result = execute_safe(['systemctl', 'is-active', 'atd'])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="atd_running",
                passed=True,
                points=3,
                message=f"atd service is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="atd_running",
                passed=False,
                points=0,
                max_points=3,
                message=f"atd service is not running"
            ))

        # Check if there are any at jobs scheduled (5 points)
        result = execute_safe(['atq'])
        if result.success and result.stdout.strip():
            checks.append(ValidationCheck(
                name="at_jobs_exist",
                passed=True,
                points=5,
                message=f"At job(s) scheduled ({len(result.stdout.strip().split('\\n'))} job(s))"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="at_jobs_exist",
                passed=False,
                points=0,
                max_points=5,
                message=f"No at jobs scheduled"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("scheduling")
class CreateSystemdTimerTask(BaseTask):
    """Create a systemd timer unit."""

    def __init__(self):
        super().__init__(
            id="sched_timer_001",
            category="scheduling",
            difficulty="exam",
            points=15
        )
        self.timer_name = None
        self.service_name = None
        self.on_calendar = None
        self.command = None

    def generate(self, **params):
        """Generate systemd timer task."""
        self.timer_name = params.get('timer_name', f'custom-task{random.randint(1,99)}')
        self.service_name = f'{self.timer_name}.service'
        self.timer_name_full = f'{self.timer_name}.timer'

        schedules = [
            ('daily', 'daily at midnight'),
            ('*-*-* 02:00:00', 'daily at 2:00 AM'),
            ('Mon *-*-* 00:00:00', 'weekly on Monday'),
        ]

        self.on_calendar = params.get('schedule', random.choice(schedules)[0])
        schedule_desc = params.get('schedule_desc', self.on_calendar)

        self.command = params.get('command', '/usr/local/bin/backup.sh')

        self.description = (
            f"Create a systemd timer:\n"
            f"  - Timer name: {self.timer_name_full}\n"
            f"  - Service name: {self.service_name}\n"
            f"  - Schedule: {schedule_desc}\n"
            f"  - Command to run: {self.command}\n"
            f"  - Create both .service and .timer files in /etc/systemd/system/\n"
            f"  - Enable and start the timer"
        )

        self.hints = [
            f"Create service: /etc/systemd/system/{self.service_name}",
            f"Create timer: /etc/systemd/system/{self.timer_name_full}",
            f"Service [Service] section: ExecStart={self.command}",
            f"Timer [Timer] section: OnCalendar={self.on_calendar}",
            "Reload systemd: systemctl daemon-reload",
            f"Enable timer: systemctl enable {self.timer_name_full}",
            f"Start timer: systemctl start {self.timer_name_full}",
            f"Check status: systemctl list-timers"
        ]

        return self

    def validate(self):
        """Validate systemd timer configuration."""
        checks = []
        total_points = 0

        import os
        from validators.file_validators import validate_file_contains

        service_path = f'/etc/systemd/system/{self.service_name}'
        timer_path = f'/etc/systemd/system/{self.timer_name_full}'

        # Check 1: Service file exists (4 points)
        if os.path.exists(service_path):
            checks.append(ValidationCheck(
                name="service_file_exists",
                passed=True,
                points=4,
                message=f"Service file exists"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="service_file_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Service file {service_path} not found"
            ))

        # Check 2: Timer file exists (4 points)
        if os.path.exists(timer_path):
            checks.append(ValidationCheck(
                name="timer_file_exists",
                passed=True,
                points=4,
                message=f"Timer file exists"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="timer_file_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Timer file {timer_path} not found"
            ))

        # Check 3: Timer is enabled (4 points)
        result = execute_safe(['systemctl', 'is-enabled', self.timer_name_full])
        if result.success and 'enabled' in result.stdout:
            checks.append(ValidationCheck(
                name="timer_enabled",
                passed=True,
                points=4,
                message=f"Timer is enabled"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="timer_enabled",
                passed=False,
                points=0,
                max_points=4,
                message=f"Timer is not enabled"
            ))

        # Check 4: Timer is active (3 points)
        result = execute_safe(['systemctl', 'is-active', self.timer_name_full])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="timer_active",
                passed=True,
                points=3,
                message=f"Timer is active"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="timer_active",
                passed=False,
                points=0,
                max_points=3,
                message=f"Timer is not active"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
