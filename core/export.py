"""
Export functionality for RHCSA Simulator.
Generates PDF and text reports of progress and exam results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from config import settings


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates progress and exam reports.

    Supports multiple formats:
    - Plain text (always available)
    - HTML (always available)
    - PDF (requires reportlab, optional)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize report generator."""
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.reports_dir = self.data_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_progress_report(self, performance_data: Dict,
                                  mistakes_data: Dict = None,
                                  format: str = 'text') -> str:
        """
        Generate a progress report.

        Args:
            performance_data: Performance statistics
            mistakes_data: Optional mistakes tracking data
            format: Output format ('text', 'html', 'pdf')

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == 'text':
            return self._generate_text_report(performance_data, mistakes_data, timestamp)
        elif format == 'html':
            return self._generate_html_report(performance_data, mistakes_data, timestamp)
        elif format == 'pdf':
            return self._generate_pdf_report(performance_data, mistakes_data, timestamp)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_text_report(self, perf: Dict, mistakes: Dict, timestamp: str) -> str:
        """Generate plain text report."""
        filepath = self.reports_dir / f"progress_report_{timestamp}.txt"

        lines = [
            "=" * 70,
            "RHCSA SIMULATOR - PROGRESS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            "OVERALL PERFORMANCE",
            "-" * 40,
            f"Total Attempts:     {perf.get('total_attempts', 0)}",
            f"Total Successes:    {perf.get('total_successes', 0)}",
            f"Success Rate:       {perf.get('overall_success_rate', 0)*100:.1f}%",
            f"Average Score:      {perf.get('overall_score_rate', 0)*100:.1f}%",
            f"Categories Practiced: {perf.get('categories_practiced', 0)}",
            f"Tasks Attempted:    {perf.get('tasks_attempted', 0)}",
            "",
        ]

        # Weak areas
        weak_cats = perf.get('weak_categories', [])
        if weak_cats:
            lines.extend([
                "WEAK AREAS (Need Improvement)",
                "-" * 40,
            ])
            for wc in weak_cats:
                lines.append(
                    f"  {wc['category'].replace('_', ' ').title()}: "
                    f"{wc['success_rate']*100:.0f}% success ({wc['attempts']} attempts)"
                )
            lines.append("")

        # Recommendations
        recs = perf.get('recommendations', [])
        if recs:
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40,
            ])
            for i, rec in enumerate(recs, 1):
                lines.append(f"  {i}. [{rec['priority'].upper()}] {rec['suggestion']}")
                lines.append(f"     Reason: {rec['reason']}")
            lines.append("")

        # Mistakes analysis
        if mistakes:
            lines.extend([
                "COMMON MISTAKES",
                "-" * 40,
            ])
            patterns = mistakes.get('patterns', {})
            for pattern, data in list(patterns.items())[:5]:
                lines.append(f"  - {data['check']} in {data['category']}: {data['count']} times")
            lines.append("")

        lines.extend([
            "=" * 70,
            "Keep practicing! Focus on your weak areas for maximum improvement.",
            "=" * 70,
        ])

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return str(filepath)

    def _generate_html_report(self, perf: Dict, mistakes: Dict, timestamp: str) -> str:
        """Generate HTML report."""
        filepath = self.reports_dir / f"progress_report_{timestamp}.html"

        success_rate = perf.get('overall_success_rate', 0) * 100
        score_rate = perf.get('overall_score_rate', 0) * 100

        # Determine color based on performance
        if success_rate >= 70:
            perf_color = '#28a745'  # Green
        elif success_rate >= 50:
            perf_color = '#ffc107'  # Yellow
        else:
            perf_color = '#dc3545'  # Red

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RHCSA Simulator - Progress Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .report {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #dc3545;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: {perf_color};
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .weak-area {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 10px 0;
        }}
        .recommendation {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 10px 15px;
            margin: 10px 0;
        }}
        .recommendation.high {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        .recommendation.medium {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: {perf_color};
            transition: width 0.3s;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.8em;
            text-align: right;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="report">
        <h1>RHCSA Simulator Progress Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Overall Performance</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{success_rate:.0f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{score_rate:.0f}%</div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{perf.get('total_attempts', 0)}</div>
                <div class="stat-label">Tasks Attempted</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{perf.get('categories_practiced', 0)}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {success_rate}%"></div>
        </div>
"""

        # Weak areas
        weak_cats = perf.get('weak_categories', [])
        if weak_cats:
            html += """
        <h2>Areas Needing Improvement</h2>
"""
            for wc in weak_cats:
                html += f"""
        <div class="weak-area">
            <strong>{wc['category'].replace('_', ' ').title()}</strong><br>
            Success Rate: {wc['success_rate']*100:.0f}% ({wc['attempts']} attempts, {wc['failures']} failures)
        </div>
"""

        # Recommendations
        recs = perf.get('recommendations', [])
        if recs:
            html += """
        <h2>Recommendations</h2>
"""
            for rec in recs:
                html += f"""
        <div class="recommendation {rec['priority']}">
            <strong>{rec['suggestion']}</strong><br>
            <small>{rec['reason']}</small>
        </div>
"""

        # Category breakdown
        html += """
        <h2>Category Breakdown</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Attempts</th>
                <th>Success Rate</th>
                <th>Status</th>
            </tr>
"""
        for wc in weak_cats:
            status = "✅ Good" if wc['success_rate'] >= 0.7 else "⚠️ Needs Work" if wc['success_rate'] >= 0.5 else "❌ Struggling"
            html += f"""
            <tr>
                <td>{wc['category'].replace('_', ' ').title()}</td>
                <td>{wc['attempts']}</td>
                <td>{wc['success_rate']*100:.0f}%</td>
                <td>{status}</td>
            </tr>
"""
        html += """
        </table>
"""

        html += """
        <hr>
        <p style="text-align: center; color: #666;">
            Keep practicing! Focus on your weak areas for the best results on exam day.
        </p>
    </div>
</body>
</html>
"""

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)

    def _generate_pdf_report(self, perf: Dict, mistakes: Dict, timestamp: str) -> str:
        """Generate PDF report (requires reportlab)."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        except ImportError:
            # Fall back to HTML if reportlab not available
            logger.warning("reportlab not installed, generating HTML instead")
            html_path = self._generate_html_report(perf, mistakes, timestamp)
            return html_path + " (PDF requires 'pip install reportlab')"

        filepath = self.reports_dir / f"progress_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Title2',
                                  parent=styles['Heading1'],
                                  fontSize=24,
                                  spaceAfter=30))

        story = []

        # Title
        story.append(Paragraph("RHCSA Simulator Progress Report", styles['Title2']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']))
        story.append(Spacer(1, 20))

        # Overall stats
        story.append(Paragraph("Overall Performance", styles['Heading2']))

        stats_data = [
            ['Metric', 'Value'],
            ['Total Attempts', str(perf.get('total_attempts', 0))],
            ['Success Rate', f"{perf.get('overall_success_rate', 0)*100:.1f}%"],
            ['Average Score', f"{perf.get('overall_score_rate', 0)*100:.1f}%"],
            ['Categories Practiced', str(perf.get('categories_practiced', 0))],
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Weak areas
        weak_cats = perf.get('weak_categories', [])
        if weak_cats:
            story.append(Paragraph("Areas Needing Improvement", styles['Heading2']))
            for wc in weak_cats:
                story.append(Paragraph(
                    f"• <b>{wc['category'].replace('_', ' ').title()}</b>: "
                    f"{wc['success_rate']*100:.0f}% success rate ({wc['attempts']} attempts)",
                    styles['Normal']))
            story.append(Spacer(1, 20))

        # Recommendations
        recs = perf.get('recommendations', [])
        if recs:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for i, rec in enumerate(recs, 1):
                story.append(Paragraph(
                    f"{i}. <b>{rec['suggestion']}</b><br/>"
                    f"<i>{rec['reason']}</i>",
                    styles['Normal']))
            story.append(Spacer(1, 20))

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            "Keep practicing! Focus on your weak areas for the best results.",
            styles['Normal']))

        doc.build(story)
        return str(filepath)

    def generate_exam_report(self, exam_result: Dict, format: str = 'text') -> str:
        """Generate an exam result report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == 'text':
            return self._generate_exam_text_report(exam_result, timestamp)
        elif format == 'html':
            return self._generate_exam_html_report(exam_result, timestamp)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_exam_text_report(self, result: Dict, timestamp: str) -> str:
        """Generate exam result text report."""
        filepath = self.reports_dir / f"exam_report_{timestamp}.txt"

        passed = result.get('passed', False)
        status = "PASSED" if passed else "FAILED"

        lines = [
            "=" * 70,
            "RHCSA SIMULATOR - EXAM RESULT",
            f"Exam ID: {result.get('exam_id', 'N/A')}",
            f"Date: {result.get('start_time', 'N/A')[:10]}",
            "=" * 70,
            "",
            f"RESULT: {status}",
            f"Score: {result.get('total_score', 0)}/{result.get('max_score', 0)} "
            f"({result.get('percentage', 0):.1f}%)",
            f"Pass Threshold: {result.get('pass_threshold', 70)}%",
            f"Tasks Completed: {result.get('tasks_passed', 0)}/{result.get('task_count', 0)}",
            "",
            "TASK BREAKDOWN",
            "-" * 40,
        ]

        for task in result.get('tasks', []):
            status_icon = "✓" if task.get('passed') else "✗"
            lines.append(
                f"  {status_icon} {task.get('task_id', 'N/A')}: "
                f"{task.get('score', 0)}/{task.get('max_score', 0)} pts"
            )

        lines.extend([
            "",
            "CATEGORY BREAKDOWN",
            "-" * 40,
        ])

        for cat, data in result.get('category_breakdown', {}).items():
            lines.append(
                f"  {cat.replace('_', ' ').title()}: "
                f"{data.get('earned_points', 0)}/{data.get('total_points', 0)} "
                f"({data.get('percentage', 0):.0f}%)"
            )

        lines.extend([
            "",
            "=" * 70,
        ])

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return str(filepath)

    def _generate_exam_html_report(self, result: Dict, timestamp: str) -> str:
        """Generate exam result HTML report."""
        filepath = self.reports_dir / f"exam_report_{timestamp}.html"

        passed = result.get('passed', False)
        percentage = result.get('percentage', 0)

        result_color = '#28a745' if passed else '#dc3545'
        result_text = 'PASSED' if passed else 'FAILED'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RHCSA Exam Result</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .result {{ text-align: center; padding: 30px; background: {result_color}; color: white; border-radius: 8px; margin: 20px 0; }}
        .result h1 {{ margin: 0; font-size: 3em; }}
        .score {{ font-size: 2em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h1>RHCSA Simulator - Exam Result</h1>
    <p>Exam ID: {result.get('exam_id', 'N/A')} | Date: {result.get('start_time', 'N/A')[:10]}</p>

    <div class="result">
        <h1>{result_text}</h1>
        <p class="score">{result.get('total_score', 0)}/{result.get('max_score', 0)} ({percentage:.1f}%)</p>
    </div>

    <h2>Task Results</h2>
    <table>
        <tr><th>Task</th><th>Category</th><th>Score</th><th>Status</th></tr>
"""

        for task in result.get('tasks', []):
            status_class = 'pass' if task.get('passed') else 'fail'
            status_icon = '✓' if task.get('passed') else '✗'
            html += f"""
        <tr>
            <td>{task.get('task_id', 'N/A')}</td>
            <td>{task.get('category', 'N/A').replace('_', ' ').title()}</td>
            <td>{task.get('score', 0)}/{task.get('max_score', 0)}</td>
            <td class="{status_class}">{status_icon}</td>
        </tr>
"""

        html += """
    </table>

    <h2>Category Breakdown</h2>
    <table>
        <tr><th>Category</th><th>Points</th><th>Percentage</th></tr>
"""

        for cat, data in result.get('category_breakdown', {}).items():
            html += f"""
        <tr>
            <td>{cat.replace('_', ' ').title()}</td>
            <td>{data.get('earned_points', 0)}/{data.get('total_points', 0)}</td>
            <td>{data.get('percentage', 0):.0f}%</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)


# Global instance
_report_generator = None


def get_report_generator() -> ReportGenerator:
    """Get global ReportGenerator instance."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
