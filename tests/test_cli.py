import json
from pathlib import Path

from agentskills_ci.cli import main


def write_good_skill(root: Path):
    skill_dir = root / "skills" / "good"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: good
description: Use when testing the CLI with a valid skill.
version: 1.0.0
---
# Good

## Overview
Useful.

## When to Use
- Testing

## Common Pitfalls
1. None.

## Verification Checklist
- [ ] Verified
""",
        encoding="utf-8",
    )


def test_cli_check_returns_zero_for_valid_skills(tmp_path: Path, capsys):
    write_good_skill(tmp_path)

    exit_code = main(["check", str(tmp_path / "skills")])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "1 skills checked" in out
    assert "Overall score" in out


def test_cli_check_json_report_contains_scores(tmp_path: Path, capsys):
    write_good_skill(tmp_path)

    exit_code = main(["check", str(tmp_path / "skills"), "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["summary"]["total"] == 1
    assert payload["results"][0]["score"] >= 90


def test_cli_min_score_controls_exit_code_and_summary(tmp_path: Path, capsys):
    skill_dir = tmp_path / "skills" / "warning-only"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: warning-only
description: Testing a warning-only skill below the default threshold.
---
# Warning Only

This skill has no error-level issues. It intentionally omits recommended sections while keeping enough body text to avoid the very-short-body warning.
""",
        encoding="utf-8",
    )

    exit_code = main(
        ["check", str(tmp_path / "skills"), "--min-score", "60", "--format", "json"]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["summary"]["passed"] == 1
    assert payload["summary"]["failed"] == 0
    assert 60 <= payload["results"][0]["score"] < 80
    assert payload["results"][0]["passed"] is True


def test_cli_init_github_action_writes_workflow(tmp_path: Path):
    exit_code = main(["init-github-action", "--repo", str(tmp_path), "--path", "skills"])

    workflow = tmp_path / ".github" / "workflows" / "agentskills-ci.yml"
    assert exit_code == 0
    assert workflow.exists()
    assert "agentskills-ci check skills" in workflow.read_text(encoding="utf-8")
