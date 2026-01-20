"""
Common mistakes tracking database for RHCSA Simulator.
Tracks user errors and provides targeted practice recommendations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from config import settings


logger = logging.getLogger(__name__)


class MistakesTracker:
    """
    Tracks common mistakes and provides analytics.
    Stores mistake patterns to help users improve weak areas.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize mistakes tracker."""
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.mistakes_file = self.data_dir / 'mistakes.json'
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load mistakes data from file."""
        if self.mistakes_file.exists():
            try:
                with open(self.mistakes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading mistakes data: {e}")

        return {
            'mistakes': [],
            'category_stats': {},
            'check_stats': {},
            'task_stats': {},
            'last_updated': None,
        }

    def _save_data(self):
        """Save mistakes data to file."""
        try:
            self.data['last_updated'] = datetime.now().isoformat()
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.mistakes_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving mistakes data: {e}")

    def record_mistake(self, task_id: str, category: str, check_name: str,
                       expected: str, actual: str, difficulty: str):
        """Record a single mistake."""
        mistake = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'category': category,
            'check_name': check_name,
            'expected': expected,
            'actual': actual,
            'difficulty': difficulty,
        }

        self.data['mistakes'].append(mistake)

        # Update category stats
        if category not in self.data['category_stats']:
            self.data['category_stats'][category] = {'total': 0, 'mistakes': 0}
        self.data['category_stats'][category]['mistakes'] += 1

        # Update check stats
        if check_name not in self.data['check_stats']:
            self.data['check_stats'][check_name] = {'total': 0, 'mistakes': 0}
        self.data['check_stats'][check_name]['mistakes'] += 1

        # Update task stats
        if task_id not in self.data['task_stats']:
            self.data['task_stats'][task_id] = {'attempts': 0, 'failures': 0}
        self.data['task_stats'][task_id]['failures'] += 1

        self._save_data()

    def record_attempt(self, task_id: str, category: str, checks: List[str]):
        """Record a task attempt (successful or not)."""
        # Update category total
        if category not in self.data['category_stats']:
            self.data['category_stats'][category] = {'total': 0, 'mistakes': 0}
        self.data['category_stats'][category]['total'] += 1

        # Update check totals
        for check_name in checks:
            if check_name not in self.data['check_stats']:
                self.data['check_stats'][check_name] = {'total': 0, 'mistakes': 0}
            self.data['check_stats'][check_name]['total'] += 1

        # Update task attempts
        if task_id not in self.data['task_stats']:
            self.data['task_stats'][task_id] = {'attempts': 0, 'failures': 0}
        self.data['task_stats'][task_id]['attempts'] += 1

        self._save_data()

    def get_weak_categories(self, min_attempts: int = 3) -> List[Dict]:
        """Get categories sorted by failure rate."""
        weak = []
        for cat, stats in self.data['category_stats'].items():
            if stats['total'] >= min_attempts:
                failure_rate = stats['mistakes'] / stats['total'] if stats['total'] > 0 else 0
                weak.append({
                    'category': cat,
                    'failure_rate': failure_rate,
                    'total_attempts': stats['total'],
                    'total_mistakes': stats['mistakes'],
                })

        return sorted(weak, key=lambda x: x['failure_rate'], reverse=True)

    def get_weak_checks(self, min_attempts: int = 2) -> List[Dict]:
        """Get validation checks sorted by failure rate."""
        weak = []
        for check, stats in self.data['check_stats'].items():
            if stats['total'] >= min_attempts:
                failure_rate = stats['mistakes'] / stats['total'] if stats['total'] > 0 else 0
                weak.append({
                    'check': check,
                    'failure_rate': failure_rate,
                    'total_attempts': stats['total'],
                    'total_mistakes': stats['mistakes'],
                })

        return sorted(weak, key=lambda x: x['failure_rate'], reverse=True)

    def get_recent_mistakes(self, limit: int = 10) -> List[Dict]:
        """Get most recent mistakes."""
        return self.data['mistakes'][-limit:][::-1]

    def get_mistake_patterns(self) -> Dict[str, List[str]]:
        """Identify common mistake patterns."""
        patterns = defaultdict(list)

        for mistake in self.data['mistakes']:
            check = mistake['check_name']
            pattern_key = f"{mistake['category']}:{check}"
            patterns[pattern_key].append(mistake)

        # Filter to patterns that occur frequently
        common_patterns = {}
        for key, mistakes in patterns.items():
            if len(mistakes) >= 2:
                common_patterns[key] = {
                    'count': len(mistakes),
                    'category': mistakes[0]['category'],
                    'check': mistakes[0]['check_name'],
                    'examples': mistakes[-3:],  # Last 3 examples
                }

        return common_patterns

    def get_recommendations(self) -> List[str]:
        """Get practice recommendations based on mistakes."""
        recommendations = []

        weak_cats = self.get_weak_categories()
        if weak_cats:
            worst = weak_cats[0]
            if worst['failure_rate'] > 0.3:
                recommendations.append(
                    f"Focus on {worst['category'].replace('_', ' ').title()}: "
                    f"{worst['failure_rate']*100:.0f}% failure rate"
                )

        weak_checks = self.get_weak_checks()
        if weak_checks:
            # Group by type
            check_types = defaultdict(list)
            for wc in weak_checks[:5]:
                if wc['failure_rate'] > 0.3:
                    check_name = wc['check']
                    if 'selinux' in check_name or 'context' in check_name or 'boolean' in check_name:
                        check_types['SELinux'].append(check_name)
                    elif 'user' in check_name or 'group' in check_name or 'uid' in check_name:
                        check_types['Users & Groups'].append(check_name)
                    elif 'service' in check_name:
                        check_types['Services'].append(check_name)
                    elif 'sudo' in check_name:
                        check_types['Sudo Configuration'].append(check_name)
                    else:
                        check_types['Other'].append(check_name)

            for category, checks in check_types.items():
                if checks:
                    recommendations.append(f"Practice {category}: struggling with {', '.join(checks[:2])}")

        patterns = self.get_mistake_patterns()
        if patterns:
            for pattern, data in list(patterns.items())[:3]:
                if data['count'] >= 3:
                    recommendations.append(
                        f"Repeated mistake: {data['check']} in {data['category']} ({data['count']} times)"
                    )

        if not recommendations:
            recommendations.append("No significant weak areas detected. Keep practicing!")

        return recommendations

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        total_mistakes = len(self.data['mistakes'])
        total_categories = len(self.data['category_stats'])

        # Calculate overall failure rate
        total_attempts = sum(s['total'] for s in self.data['category_stats'].values())
        total_failures = sum(s['mistakes'] for s in self.data['category_stats'].values())
        overall_rate = total_failures / total_attempts if total_attempts > 0 else 0

        return {
            'total_mistakes': total_mistakes,
            'total_attempts': total_attempts,
            'overall_failure_rate': overall_rate,
            'categories_practiced': total_categories,
            'weak_areas': self.get_weak_categories()[:3],
            'recommendations': self.get_recommendations(),
        }

    def clear_data(self):
        """Clear all mistake data."""
        self.data = {
            'mistakes': [],
            'category_stats': {},
            'check_stats': {},
            'task_stats': {},
            'last_updated': None,
        }
        self._save_data()


# Global instance
_tracker = None


def get_mistakes_tracker() -> MistakesTracker:
    """Get global MistakesTracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = MistakesTracker()
    return _tracker
