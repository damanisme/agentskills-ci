from pathlib import Path

from agentskills_ci.parser import parse_skill_file
from agentskills_ci.validators import validate_skill


def make_skill(tmp_path: Path, content: str, extra_files=None):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    for relative, body in (extra_files or {}).items():
        path = skill_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    return parse_skill_file(skill_file)


def test_validate_good_skill_passes_with_high_score(tmp_path: Path):
    skill = make_skill(
        tmp_path,
        """---
name: good-skill
description: Use when testing a well-structured AI-agent skill.
version: 1.0.0
metadata:
  hermes:
    tags: [testing, skills]
---
# Good Skill

## Overview
This skill has enough structure to be useful.

## When to Use
- When validating examples

## Common Pitfalls
1. Forgetting to test.

## Verification Checklist
- [ ] Tests pass

See `references/guide.md`.
""",
        {"references/guide.md": "# Guide\n"},
    )

    result = validate_skill(skill)

    assert result.passed
    assert result.score >= 90
    assert result.issues == []


def test_validate_flags_missing_frontmatter_and_body_sections(tmp_path: Path):
    skill = make_skill(
        tmp_path,
        """---
name: weak-skill
---
# Weak
No useful sections.
""",
    )

    result = validate_skill(skill)

    messages = [issue.message for issue in result.issues]
    assert not result.passed
    assert "Missing required frontmatter field: description" in messages
    assert any("Missing recommended section" in message for message in messages)
    assert result.score < 80


def test_validate_flags_missing_linked_files_and_risky_commands(tmp_path: Path):
    skill = make_skill(
        tmp_path,
        """---
name: risky-skill
description: Use when demonstrating risky shell instructions.
---
# Risky

## When to Use
- Demo

Run `rm -rf /tmp/something` and then post to Twitter.
See `scripts/missing.sh`.
""",
    )

    result = validate_skill(skill)

    assert any("Referenced path does not exist: scripts/missing.sh" == i.message for i in result.issues)
    assert any("Risky command pattern found: rm -rf" == i.message for i in result.issues)
    assert any("Side-effect instruction lacks an approval gate" in i.message for i in result.issues)
