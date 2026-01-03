"""
Results tracking and persistence for RHCSA Simulator.
Saves exam results to JSON files and provides progress tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from config import settings
from utils.helpers import generate_id


logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of a single task."""
    task_id: str
    category: str
    difficulty: str
    description: str
    score: int
    max_score: int
    passed: bool
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExamResult:
    """Complete exam result."""
    exam_id: str
    start_time: str
    end_time: str
    duration_seconds: int
    timer_enabled: bool
    task_results: List[TaskResult]
    total_score: int
    max_score: int
    passed: bool
    pass_threshold: float = 0.70

    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.total_score / self.max_score) * 100

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'exam_id': self.exam_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_seconds': self.duration_seconds,
            'timer_enabled': self.timer_enabled,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'passed': self.passed,
            'pass_threshold': self.pass_threshold * 100,
            'task_count': len(self.task_results),
            'tasks_passed': sum(1 for t in self.task_results if t.passed),
            'tasks': [asdict(t) for t in self.task_results],
            'category_breakdown': self.get_category_breakdown()
        }

    def get_category_breakdown(self):
        """Get score breakdown by category."""
        breakdown = {}
        for task in self.task_results:
            if task.category not in breakdown:
                breakdown[task.category] = {
                    'total_points': 0,
                    'earned_points': 0,
                    'tasks': 0,
                    'passed': 0
                }
            breakdown[task.category]['total_points'] += task.max_score
            breakdown[task.category]['earned_points'] += task.score
            breakdown[task.category]['tasks'] += 1
            if task.passed:
                breakdown[task.category]['passed'] += 1

        # Calculate percentages
        for category in breakdown:
            total = breakdown[category]['total_points']
            earned = breakdown[category]['earned_points']
            breakdown[category]['percentage'] = (earned / total * 100) if total > 0 else 0

        return breakdown


class ResultsManager:
    """
    Manages exam results persistence and retrieval.
    """

    def __init__(self, results_dir=None):
        """
        Initialize results manager.

        Args:
            results_dir (Path): Directory for results (default: from settings)
        """
        self.results_dir = Path(results_dir or settings.RESULTS_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def save_result(self, exam_result):
        """
        Save exam result to JSON file.

        Args:
            exam_result (ExamResult): Exam result to save

        Returns:
            Path: Path to saved file
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{settings.RESULT_FILE_PREFIX}{timestamp}_{exam_result.exam_id}.json"
            filepath = self.results_dir / filename

            # Convert to dict and save
            data = exam_result.to_dict()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Saved exam result to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error saving result: {e}")
            return None

    def load_results(self, limit=10):
        """
        Load recent exam results.

        Args:
            limit (int): Maximum number of results to load

        Returns:
            list: List of exam result dictionaries
        """
        try:
            # Get all result files
            result_files = sorted(
                self.results_dir.glob(f"{settings.RESULT_FILE_PREFIX}*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            results = []
            for filepath in result_files[:limit]:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        results.append(data)
                except Exception as e:
                    self.logger.warning(f"Could not load {filepath}: {e}")

            return results

        except Exception as e:
            self.logger.error(f"Error loading results: {e}")
            return []

    def get_statistics(self):
        """
        Calculate overall statistics from all results.

        Returns:
            dict: Statistics
        """
        results = self.load_results(limit=100)

        if not results:
            return {
                'total_exams': 0,
                'average_score': 0.0,
                'pass_rate': 0.0,
                'best_score': 0.0,
                'latest_score': 0.0
            }

        total_exams = len(results)
        scores = [r['percentage'] for r in results]
        passed_count = sum(1 for r in results if r['passed'])

        return {
            'total_exams': total_exams,
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'pass_rate': (passed_count / total_exams * 100) if total_exams > 0 else 0.0,
            'best_score': max(scores) if scores else 0.0,
            'latest_score': scores[0] if scores else 0.0
        }

    def display_progress(self):
        """Display progress and statistics."""
        from utils.formatters import print_header, print_table, success, error, bold

        stats = self.get_statistics()

        print_header("Your Progress")

        if stats['total_exams'] == 0:
            print("No exam results yet. Take an exam to see your progress!")
            return

        print(bold("Overall Statistics:"))
        print(f"  Total exams taken: {stats['total_exams']}")
        print(f"  Average score: {stats['average_score']:.1f}%")
        print(f"  Pass rate: {stats['pass_rate']:.1f}%")
        print(f"  Best score: {stats['best_score']:.1f}%")
        print(f"  Latest score: {stats['latest_score']:.1f}%")
        print()

        # Show recent results
        recent = self.load_results(limit=5)
        if recent:
            print(bold("Recent Exams:"))
            rows = []
            for r in recent:
                date = r['start_time'][:10]  # Extract date
                score = f"{r['percentage']:.0f}%"
                status = success("PASS") if r['passed'] else error("FAIL")
                tasks = f"{r['tasks_passed']}/{r['task_count']}"
                rows.append([date, score, tasks, status])

            print_table(['Date', 'Score', 'Tasks', 'Status'], rows)


# Global results manager
_results_manager = None


def get_results_manager():
    """
    Get global ResultsManager instance.

    Returns:
        ResultsManager: Global manager
    """
    global _results_manager
    if _results_manager is None:
        _results_manager = ResultsManager()
    return _results_manager
