"""
Essential tools tasks for RHCSA exam (find, grep, tar, I/O redirection).
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.safe_executor import execute_safe
from validators.file_validators import validate_file_exists, validate_file_contains
from validators.system_validators import validate_archive_contains, get_archive_compression


logger = logging.getLogger(__name__)


@TaskRegistry.register("essential_tools")
class FindFilesTask(BaseTask):
    """Find files using the find command."""

    def __init__(self):
        super().__init__(
            id="tools_find_001",
            category="essential_tools",
            difficulty="medium",
            points=10
        )
        self.criteria = None
        self.search_path = None
        self.output_file = None

    def generate(self, **params):
        """Generate find task."""
        criteria_options = [
            ('-name "*.log"', 'all files ending with .log'),
            ('-type d', 'all directories'),
            ('-user root', 'all files owned by root'),
            ('-size +10M', 'files larger than 10MB'),
            ('-mtime -7', 'files modified in last 7 days'),
            ('-perm 777', 'files with 777 permissions'),
        ]

        self.search_path = params.get('path', '/etc')
        criteria_choice = params.get('criteria', random.choice(criteria_options))

        if isinstance(criteria_choice, tuple):
            self.criteria, criteria_desc = criteria_choice
        else:
            self.criteria = criteria_choice
            criteria_desc = criteria_choice

        self.output_file = params.get('output', '/tmp/findresults.txt')

        self.description = (
            f"Use find command to locate files:\n"
            f"  - Search path: {self.search_path}\n"
            f"  - Criteria: {criteria_desc}\n"
            f"  - Save results to: {self.output_file}\n"
            f"  - Redirect output to the file"
        )

        self.hints = [
            f"Use find: find {self.search_path} {self.criteria}",
            f"Save to file: find {self.search_path} {self.criteria} > {self.output_file}",
            "Common find options: -name, -type, -user, -size, -mtime, -perm",
            "-type f = files, -type d = directories",
            "Sizes: -size +10M (larger than), -size -10M (smaller than)"
        ]

        return self

    def validate(self):
        """Validate find results."""
        checks = []
        total_points = 0

        # Check: Output file exists and has content
        if validate_file_exists(self.output_file):
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=True,
                points=5,
                message=f"Output file {self.output_file} exists"
            ))
            total_points += 5

            # Check if file has content
            try:
                with open(self.output_file, 'r') as f:
                    content = f.read()
                    if content.strip():
                        checks.append(ValidationCheck(
                            name="has_results",
                            passed=True,
                            points=5,
                            message=f"File contains search results"
                        ))
                        total_points += 5
                    else:
                        checks.append(ValidationCheck(
                            name="has_results",
                            passed=False,
                            points=0,
                            message=f"File is empty"
                        ))
            except Exception as e:
                checks.append(ValidationCheck(
                    name="has_results",
                    passed=False,
                    points=0,
                    message=f"Could not read file: {e}"
                ))
        else:
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=False,
                points=0,
                message=f"Output file {self.output_file} not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("essential_tools")
class GrepSearchTask(BaseTask):
    """Search for patterns in files using grep."""

    def __init__(self):
        super().__init__(
            id="tools_grep_001",
            category="essential_tools",
            difficulty="easy",
            points=8
        )
        self.pattern = None
        self.search_file = None
        self.output_file = None

    def generate(self, **params):
        """Generate grep task."""
        patterns = ['error', 'warning', 'failed', 'root', 'deny']
        self.pattern = params.get('pattern', random.choice(patterns))
        self.search_file = params.get('search_file', '/var/log/messages')
        self.output_file = params.get('output', '/tmp/grepresults.txt')

        self.description = (
            f"Search for pattern in a file:\n"
            f"  - Pattern: '{self.pattern}'\n"
            f"  - Search in: {self.search_file}\n"
            f"  - Save matching lines to: {self.output_file}\n"
            f"  - Use case-insensitive search"
        )

        self.hints = [
            f"Use grep: grep -i '{self.pattern}' {self.search_file}",
            f"Save to file: grep -i '{self.pattern}' {self.search_file} > {self.output_file}",
            "-i makes search case-insensitive",
            "-v inverts match (lines NOT containing pattern)",
            "-r searches recursively in directories",
            "-n shows line numbers"
        ]

        return self

    def validate(self):
        """Validate grep results."""
        checks = []
        total_points = 0

        if validate_file_exists(self.output_file):
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=True,
                points=4,
                message=f"Output file exists"
            ))
            total_points += 4

            # Check if pattern appears in output
            if validate_file_contains(self.output_file, self.pattern, case_sensitive=False):
                checks.append(ValidationCheck(
                    name="pattern_found",
                    passed=True,
                    points=4,
                    message=f"Output contains the pattern '{self.pattern}'"
                ))
                total_points += 4
            else:
                checks.append(ValidationCheck(
                    name="pattern_found",
                    passed=True,
                    points=2,
                    message=f"Output file exists (pattern may not be present in source, partial credit)"
                ))
                total_points += 2
        else:
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=False,
                points=0,
                message=f"Output file not found"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("essential_tools")
class CreateArchiveTask(BaseTask):
    """Create a tar archive with compression."""

    def __init__(self):
        super().__init__(
            id="tools_tar_001",
            category="essential_tools",
            difficulty="medium",
            points=12
        )
        self.archive_path = None
        self.source_path = None
        self.compression = None

    def generate(self, **params):
        """Generate tar archive task."""
        compressions = [
            ('gzip', 'gz', 'z', 'gzip'),
            ('bzip2', 'bz2', 'j', 'bzip2'),
            ('xz', 'xz', 'J', 'xz'),
        ]

        comp_choice = params.get('compression', random.choice(compressions))
        if isinstance(comp_choice, tuple):
            comp_name, comp_ext, comp_flag, self.compression = comp_choice
        else:
            comp_name = comp_choice
            comp_ext = comp_choice
            comp_flag = 'z' if comp_choice == 'gzip' else 'j'
            self.compression = comp_choice

        self.source_path = params.get('source', '/etc/sysconfig')
        self.archive_path = params.get('archive', f'/tmp/backup.tar.{comp_ext}')

        self.description = (
            f"Create a compressed archive:\n"
            f"  - Source directory: {self.source_path}\n"
            f"  - Archive file: {self.archive_path}\n"
            f"  - Compression: {comp_name}\n"
            f"  - Use tar command"
        )

        self.hints = [
            f"Create archive: tar -c{comp_flag}f {self.archive_path} {self.source_path}",
            "c = create, z = gzip, j = bzip2, J = xz, f = file",
            f"Example: tar -czf {self.archive_path} {self.source_path}",
            "List contents: tar -tf {archive}",
            "Extract: tar -xf {archive}"
        ]

        return self

    def validate(self):
        """Validate tar archive creation."""
        checks = []
        total_points = 0

        # Check 1: Archive file exists (5 points)
        if validate_file_exists(self.archive_path):
            checks.append(ValidationCheck(
                name="archive_exists",
                passed=True,
                points=5,
                message=f"Archive file exists"
            ))
            total_points += 5

            # Check 2: Archive has correct compression (4 points)
            actual_compression = get_archive_compression(self.archive_path)
            if actual_compression == self.compression:
                checks.append(ValidationCheck(
                    name="correct_compression",
                    passed=True,
                    points=4,
                    message=f"Archive has correct compression: {self.compression}"
                ))
                total_points += 4
            elif actual_compression:
                checks.append(ValidationCheck(
                    name="correct_compression",
                    passed=True,
                    points=2,
                    message=f"Archive is compressed but with {actual_compression} (partial credit)"
                ))
                total_points += 2
            else:
                checks.append(ValidationCheck(
                    name="correct_compression",
                    passed=False,
                    points=0,
                    message=f"Could not determine compression type"
                ))

            # Check 3: Archive is valid tar file (3 points)
            result = execute_safe(['tar', '-tf', self.archive_path])
            if result.success:
                checks.append(ValidationCheck(
                    name="valid_archive",
                    passed=True,
                    points=3,
                    message=f"Archive is a valid tar file"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="valid_archive",
                    passed=False,
                    points=0,
                    message=f"Archive is not a valid tar file"
                ))
        else:
            checks.append(ValidationCheck(
                name="archive_exists",
                passed=False,
                points=0,
                message=f"Archive file not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("essential_tools")
class ExtractArchiveTask(BaseTask):
    """Extract a tar archive to a specific location."""

    def __init__(self):
        super().__init__(
            id="tools_extract_001",
            category="essential_tools",
            difficulty="easy",
            points=8
        )
        self.archive_path = None
        self.extract_path = None
        self.expected_file = None

    def generate(self, **params):
        """Generate archive extraction task."""
        self.archive_path = params.get('archive', '/tmp/backup.tar.gz')
        self.extract_path = params.get('extract_to', '/tmp/extracted')
        self.expected_file = params.get('expected_file', 'README')

        self.description = (
            f"Extract an archive:\n"
            f"  - Archive: {self.archive_path}\n"
            f"  - Extract to: {self.extract_path}\n"
            f"  - Create extraction directory if needed\n"
            f"  - Verify extraction was successful"
        )

        self.hints = [
            f"Create directory: mkdir -p {self.extract_path}",
            f"Extract: tar -xf {self.archive_path} -C {self.extract_path}",
            "-x = extract, -C specifies destination directory",
            "Auto-detects compression type",
            "List before extracting: tar -tf {archive}"
        ]

        return self

    def validate(self):
        """Validate archive extraction."""
        checks = []
        total_points = 0

        import os

        # Check 1: Extract directory exists (3 points)
        if os.path.exists(self.extract_path) and os.path.isdir(self.extract_path):
            checks.append(ValidationCheck(
                name="extract_dir_exists",
                passed=True,
                points=3,
                message=f"Extraction directory exists"
            ))
            total_points += 3

            # Check 2: Directory has content (5 points)
            try:
                contents = os.listdir(self.extract_path)
                if contents:
                    checks.append(ValidationCheck(
                        name="files_extracted",
                        passed=True,
                        points=5,
                        message=f"Files extracted ({len(contents)} items found)"
                    ))
                    total_points += 5
                else:
                    checks.append(ValidationCheck(
                        name="files_extracted",
                        passed=False,
                        points=0,
                        message=f"Extract directory is empty"
                    ))
            except Exception as e:
                checks.append(ValidationCheck(
                    name="files_extracted",
                    passed=False,
                    points=0,
                    message=f"Could not list directory: {e}"
                ))
        else:
            checks.append(ValidationCheck(
                name="extract_dir_exists",
                passed=False,
                points=0,
                message=f"Extract directory not found"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("essential_tools")
class IORedirectionTask(BaseTask):
    """Use I/O redirection and pipes."""

    def __init__(self):
        super().__init__(
            id="tools_io_001",
            category="essential_tools",
            difficulty="exam",
            points=12
        )
        self.source_file = None
        self.output_file = None
        self.operation = None

    def generate(self, **params):
        """Generate I/O redirection task."""
        operations = [
            ('sort_unique', 'Sort lines and remove duplicates'),
            ('count_lines', 'Count number of lines'),
            ('find_pattern', 'Find and count pattern occurrences'),
        ]

        self.source_file = params.get('source', '/etc/passwd')
        self.output_file = params.get('output', '/tmp/processed.txt')

        if params.get('operation'):
            self.operation = params['operation']
            op_desc = params.get('operation_desc', self.operation)
        else:
            self.operation, op_desc = random.choice(operations)

        if self.operation == 'sort_unique':
            task_details = f"  - Sort all lines alphabetically\n  - Remove duplicate lines\n  - Save to {self.output_file}"
            example = f"sort {self.source_file} | uniq > {self.output_file}"
        elif self.operation == 'count_lines':
            task_details = f"  - Count total number of lines\n  - Save count to {self.output_file}"
            example = f"wc -l {self.source_file} > {self.output_file}"
        else:  # find_pattern
            task_details = f"  - Count lines containing 'root'\n  - Save count to {self.output_file}"
            example = f"grep -c 'root' {self.source_file} > {self.output_file}"

        self.description = (
            f"Process a file using pipes and redirection:\n"
            f"  - Source file: {self.source_file}\n"
            f"{task_details}"
        )

        self.hints = [
            f"Example: {example}",
            "> redirects output to file (overwrites)",
            ">> appends to file",
            "| pipes output from one command to another",
            "2> redirects errors",
            "wc -l counts lines, sort sorts, uniq removes duplicates"
        ]

        return self

    def validate(self):
        """Validate I/O redirection."""
        checks = []
        total_points = 0

        # Check: Output file exists and has content
        if validate_file_exists(self.output_file):
            checks.append(ValidationCheck(
                name="output_exists",
                passed=True,
                points=6,
                message=f"Output file created"
            ))
            total_points += 6

            try:
                with open(self.output_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        checks.append(ValidationCheck(
                            name="has_content",
                            passed=True,
                            points=6,
                            message=f"Output file contains processed data"
                        ))
                        total_points += 6
                    else:
                        checks.append(ValidationCheck(
                            name="has_content",
                            passed=False,
                            points=0,
                            message=f"Output file is empty"
                        ))
            except Exception as e:
                checks.append(ValidationCheck(
                    name="has_content",
                    passed=False,
                    points=0,
                    message=f"Could not read file: {e}"
                ))
        else:
            checks.append(ValidationCheck(
                name="output_exists",
                passed=False,
                points=0,
                message=f"Output file not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
