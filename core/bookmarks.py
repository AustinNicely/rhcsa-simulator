"""
Bookmarks and weak area reporting system for RHCSA Simulator.
Allows users to bookmark tasks and get targeted practice recommendations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from config import settings


logger = logging.getLogger(__name__)


@dataclass
class Bookmark:
    """A bookmarked task."""
    task_id: str
    category: str
    difficulty: str
    description: str
    note: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceRecord:
    """Record of performance on a task/category."""
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    total_points_possible: int = 0
    total_points_earned: int = 0
    last_attempt: Optional[str] = None
    avg_time_seconds: float = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts

    @property
    def score_rate(self) -> float:
        """Calculate average score percentage."""
        if self.total_points_possible == 0:
            return 0.0
        return self.total_points_earned / self.total_points_possible


class BookmarkManager:
    """Manages bookmarked tasks."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize bookmark manager."""
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.bookmarks_file = self.data_dir / 'bookmarks.json'
        self.bookmarks: Dict[str, Bookmark] = {}
        self._load()

    def _load(self):
        """Load bookmarks from file."""
        if self.bookmarks_file.exists():
            try:
                with open(self.bookmarks_file, 'r') as f:
                    data = json.load(f)
                    for task_id, bm_data in data.items():
                        self.bookmarks[task_id] = Bookmark(**bm_data)
            except Exception as e:
                logger.error(f"Error loading bookmarks: {e}")

    def _save(self):
        """Save bookmarks to file."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.bookmarks_file, 'w') as f:
                json.dump({tid: asdict(bm) for tid, bm in self.bookmarks.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")

    def add(self, task_id: str, category: str, difficulty: str,
            description: str, note: str = "", tags: List[str] = None):
        """Add a bookmark."""
        self.bookmarks[task_id] = Bookmark(
            task_id=task_id,
            category=category,
            difficulty=difficulty,
            description=description,
            note=note,
            tags=tags or []
        )
        self._save()

    def remove(self, task_id: str):
        """Remove a bookmark."""
        if task_id in self.bookmarks:
            del self.bookmarks[task_id]
            self._save()

    def is_bookmarked(self, task_id: str) -> bool:
        """Check if a task is bookmarked."""
        return task_id in self.bookmarks

    def get(self, task_id: str) -> Optional[Bookmark]:
        """Get a bookmark by task ID."""
        return self.bookmarks.get(task_id)

    def get_all(self) -> List[Bookmark]:
        """Get all bookmarks."""
        return list(self.bookmarks.values())

    def get_by_category(self, category: str) -> List[Bookmark]:
        """Get bookmarks filtered by category."""
        return [bm for bm in self.bookmarks.values() if bm.category == category]

    def get_by_tag(self, tag: str) -> List[Bookmark]:
        """Get bookmarks filtered by tag."""
        return [bm for bm in self.bookmarks.values() if tag in bm.tags]

    def update_note(self, task_id: str, note: str):
        """Update bookmark note."""
        if task_id in self.bookmarks:
            self.bookmarks[task_id].note = note
            self._save()

    def add_tag(self, task_id: str, tag: str):
        """Add a tag to a bookmark."""
        if task_id in self.bookmarks and tag not in self.bookmarks[task_id].tags:
            self.bookmarks[task_id].tags.append(tag)
            self._save()

    def clear(self):
        """Clear all bookmarks."""
        self.bookmarks.clear()
        self._save()


class WeakAreaAnalyzer:
    """Analyzes performance to identify weak areas."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize analyzer."""
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.performance_file = self.data_dir / 'performance.json'
        self.category_performance: Dict[str, PerformanceRecord] = {}
        self.task_performance: Dict[str, PerformanceRecord] = {}
        self.check_performance: Dict[str, PerformanceRecord] = {}
        self._load()

    def _load(self):
        """Load performance data."""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    for cat, perf in data.get('categories', {}).items():
                        self.category_performance[cat] = PerformanceRecord(**perf)
                    for task, perf in data.get('tasks', {}).items():
                        self.task_performance[task] = PerformanceRecord(**perf)
                    for check, perf in data.get('checks', {}).items():
                        self.check_performance[check] = PerformanceRecord(**perf)
            except Exception as e:
                logger.error(f"Error loading performance data: {e}")

    def _save(self):
        """Save performance data."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            data = {
                'categories': {cat: asdict(perf) for cat, perf in self.category_performance.items()},
                'tasks': {task: asdict(perf) for task, perf in self.task_performance.items()},
                'checks': {check: asdict(perf) for check, perf in self.check_performance.items()},
                'last_updated': datetime.now().isoformat(),
            }
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")

    def record_attempt(self, task_id: str, category: str, passed: bool,
                       points_earned: int, points_possible: int,
                       check_results: Dict[str, bool], time_seconds: float = 0):
        """Record a task attempt."""
        timestamp = datetime.now().isoformat()

        # Update category performance
        if category not in self.category_performance:
            self.category_performance[category] = PerformanceRecord()
        cat_perf = self.category_performance[category]
        cat_perf.attempts += 1
        if passed:
            cat_perf.successes += 1
        else:
            cat_perf.failures += 1
        cat_perf.total_points_possible += points_possible
        cat_perf.total_points_earned += points_earned
        cat_perf.last_attempt = timestamp

        # Update task performance
        if task_id not in self.task_performance:
            self.task_performance[task_id] = PerformanceRecord()
        task_perf = self.task_performance[task_id]
        task_perf.attempts += 1
        if passed:
            task_perf.successes += 1
        else:
            task_perf.failures += 1
        task_perf.total_points_possible += points_possible
        task_perf.total_points_earned += points_earned
        task_perf.last_attempt = timestamp
        if time_seconds > 0:
            # Running average
            task_perf.avg_time_seconds = (
                (task_perf.avg_time_seconds * (task_perf.attempts - 1) + time_seconds)
                / task_perf.attempts
            )

        # Update check performance
        for check_name, check_passed in check_results.items():
            if check_name not in self.check_performance:
                self.check_performance[check_name] = PerformanceRecord()
            check_perf = self.check_performance[check_name]
            check_perf.attempts += 1
            if check_passed:
                check_perf.successes += 1
            else:
                check_perf.failures += 1
            check_perf.last_attempt = timestamp

        self._save()

    def get_weak_categories(self, min_attempts: int = 3) -> List[Dict]:
        """Get categories sorted by weakness (lowest success rate first)."""
        weak = []
        for cat, perf in self.category_performance.items():
            if perf.attempts >= min_attempts:
                weak.append({
                    'category': cat,
                    'success_rate': perf.success_rate,
                    'score_rate': perf.score_rate,
                    'attempts': perf.attempts,
                    'failures': perf.failures,
                })

        return sorted(weak, key=lambda x: x['success_rate'])

    def get_weak_checks(self, min_attempts: int = 2) -> List[Dict]:
        """Get validation checks sorted by weakness."""
        weak = []
        for check, perf in self.check_performance.items():
            if perf.attempts >= min_attempts:
                weak.append({
                    'check': check,
                    'success_rate': perf.success_rate,
                    'attempts': perf.attempts,
                    'failures': perf.failures,
                })

        return sorted(weak, key=lambda x: x['success_rate'])

    def get_struggling_tasks(self, min_attempts: int = 2) -> List[Dict]:
        """Get tasks the user is struggling with."""
        struggling = []
        for task_id, perf in self.task_performance.items():
            if perf.attempts >= min_attempts and perf.success_rate < 0.5:
                struggling.append({
                    'task_id': task_id,
                    'success_rate': perf.success_rate,
                    'attempts': perf.attempts,
                    'failures': perf.failures,
                })

        return sorted(struggling, key=lambda x: x['success_rate'])

    def get_recommendations(self, count: int = 5) -> List[Dict]:
        """Get practice recommendations based on weak areas."""
        recommendations = []

        # Weak categories
        weak_cats = self.get_weak_categories()
        for wc in weak_cats[:2]:
            if wc['success_rate'] < 0.7:
                recommendations.append({
                    'type': 'category',
                    'target': wc['category'],
                    'reason': f"Low success rate: {wc['success_rate']*100:.0f}%",
                    'priority': 'high' if wc['success_rate'] < 0.5 else 'medium',
                    'suggestion': f"Practice more {wc['category'].replace('_', ' ').title()} tasks",
                })

        # Struggling tasks
        struggling = self.get_struggling_tasks()
        for task in struggling[:2]:
            recommendations.append({
                'type': 'task',
                'target': task['task_id'],
                'reason': f"Failed {task['failures']} times",
                'priority': 'high',
                'suggestion': f"Review and retry task: {task['task_id']}",
            })

        # Weak checks (specific skills)
        weak_checks = self.get_weak_checks()
        check_categories = defaultdict(list)
        for wc in weak_checks[:5]:
            if wc['success_rate'] < 0.6:
                # Group checks by skill area
                check_name = wc['check']
                if 'selinux' in check_name or 'context' in check_name:
                    check_categories['SELinux'].append(check_name)
                elif 'user' in check_name or 'group' in check_name:
                    check_categories['User Management'].append(check_name)
                elif 'service' in check_name:
                    check_categories['Services'].append(check_name)
                elif 'permission' in check_name or 'mode' in check_name:
                    check_categories['Permissions'].append(check_name)

        for skill_area, checks in check_categories.items():
            recommendations.append({
                'type': 'skill',
                'target': skill_area,
                'reason': f"Struggling with: {', '.join(checks[:2])}",
                'priority': 'medium',
                'suggestion': f"Focus on {skill_area} fundamentals",
            })

        return recommendations[:count]

    def get_summary_report(self) -> Dict:
        """Get a summary report of performance."""
        total_attempts = sum(p.attempts for p in self.category_performance.values())
        total_successes = sum(p.successes for p in self.category_performance.values())
        total_points_possible = sum(p.total_points_possible for p in self.category_performance.values())
        total_points_earned = sum(p.total_points_earned for p in self.category_performance.values())

        return {
            'total_attempts': total_attempts,
            'total_successes': total_successes,
            'overall_success_rate': total_successes / total_attempts if total_attempts > 0 else 0,
            'overall_score_rate': total_points_earned / total_points_possible if total_points_possible > 0 else 0,
            'categories_practiced': len(self.category_performance),
            'tasks_attempted': len(self.task_performance),
            'weak_categories': self.get_weak_categories()[:3],
            'weak_checks': self.get_weak_checks()[:5],
            'recommendations': self.get_recommendations(),
        }

    def clear(self):
        """Clear all performance data."""
        self.category_performance.clear()
        self.task_performance.clear()
        self.check_performance.clear()
        self._save()


# Global instances
_bookmark_manager = None
_weak_area_analyzer = None


def get_bookmark_manager() -> BookmarkManager:
    """Get global BookmarkManager instance."""
    global _bookmark_manager
    if _bookmark_manager is None:
        _bookmark_manager = BookmarkManager()
    return _bookmark_manager


def get_weak_area_analyzer() -> WeakAreaAnalyzer:
    """Get global WeakAreaAnalyzer instance."""
    global _weak_area_analyzer
    if _weak_area_analyzer is None:
        _weak_area_analyzer = WeakAreaAnalyzer()
    return _weak_area_analyzer
