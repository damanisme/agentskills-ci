from __future__ import annotations

import json
from statistics import mean

from .validators import ValidationResult


def summarize(results: list[ValidationResult]) -> dict:
    scores = [result.score for result in results]
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed),
        "failed": sum(1 for result in results if not result.passed),
        "overall_score": round(mean(scores)) if scores else 0,
    }


def render_text(results: list[ValidationResult]) -> str:
    summary = summarize(results)
    status = "✅" if summary["failed"] == 0 else "⚠️"
    lines = [
        f"{status} {summary['total']} skills checked",
        f"✅ {summary['passed']} passed",
        f"⚠️  {summary['failed']} need fixes",
        "",
        f"Overall score: {summary['overall_score']}/100",
    ]
    top_issues = [(result.skill.name, issue) for result in results for issue in result.issues]
    if top_issues:
        lines.extend(["", "Top issues:"])
        for name, issue in top_issues[:20]:
            lines.append(f"- {name}: {issue.message}")
    return "\n".join(lines) + "\n"


def render_markdown(results: list[ValidationResult]) -> str:
    summary = summarize(results)
    lines = [
        "# Agent Skills CI Report",
        "",
        f"- Total: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Overall score: **{summary['overall_score']}/100**",
        "",
        "## Results",
        "",
    ]
    for result in results:
        icon = "✅" if result.passed else "⚠️"
        lines.append(f"### {icon} {result.skill.name} — {result.score}/100")
        if result.issues:
            for issue in result.issues:
                lines.append(f"- **{issue.severity}**: {issue.message}")
        else:
            lines.append("- No issues found.")
        lines.append("")
    return "\n".join(lines)


def render_json(results: list[ValidationResult]) -> str:
    payload = {
        "summary": summarize(results),
        "results": [result.to_dict() for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
