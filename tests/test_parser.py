from pathlib import Path

from agentskills_ci.parser import parse_skill_file, discover_skill_files


def test_parse_skill_file_extracts_frontmatter_body_and_links(tmp_path: Path):
    skill_dir = tmp_path / "skills" / "github-review"
    refs = skill_dir / "references"
    refs.mkdir(parents=True)
    (refs / "checklist.md").write_text("# Checklist\n", encoding="utf-8")
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        """---
name: github-review
description: Use when reviewing GitHub pull requests for quality and safety.
version: 1.0.0
metadata:
  hermes:
    tags: [github, review]
---
# GitHub Review

See `references/checklist.md`.

## When to Use
- Reviewing PRs

## Verification Checklist
- [ ] Tests pass
""",
        encoding="utf-8",
    )

    skill = parse_skill_file(skill_file)

    assert skill.name == "github-review"
    assert skill.frontmatter["description"].startswith("Use when")
    assert "# GitHub Review" in skill.body
    assert skill.referenced_paths == [Path("references/checklist.md")]


def test_discover_skill_files_finds_nested_skill_md(tmp_path: Path):
    (tmp_path / "skills" / "one").mkdir(parents=True)
    (tmp_path / "skills" / "one" / "SKILL.md").write_text(
        "---\nname: one\ndescription: ok\n---\n# One", encoding="utf-8"
    )
    (tmp_path / "skills" / "two").mkdir(parents=True)
    (tmp_path / "skills" / "two" / "SKILL.md").write_text(
        "---\nname: two\ndescription: ok\n---\n# Two", encoding="utf-8"
    )

    found = discover_skill_files(tmp_path / "skills")

    assert [p.parent.name for p in found] == ["one", "two"]


def test_discover_skill_files_follows_symlinked_skill_dirs(tmp_path: Path):
    # A real skill living outside the scanned tree...
    external = tmp_path / "external" / "linked"
    external.mkdir(parents=True)
    (external / "SKILL.md").write_text(
        "---\nname: linked\ndescription: ok\n---\n# Linked", encoding="utf-8"
    )
    # ...aggregated into the skills folder via a directory symlink.
    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "linked").symlink_to(external, target_is_directory=True)

    found = discover_skill_files(skills)

    assert [p.parent.name for p in found] == ["linked"]


def test_discover_skill_files_survives_symlink_cycle(tmp_path: Path):
    skills = tmp_path / "skills"
    one = skills / "one"
    one.mkdir(parents=True)
    (one / "SKILL.md").write_text(
        "---\nname: one\ndescription: ok\n---\n# One", encoding="utf-8"
    )
    # A directory that links back to its parent would loop without cycle protection.
    (one / "loop").symlink_to(skills, target_is_directory=True)

    found = discover_skill_files(skills)

    assert [p.parent.name for p in found] == ["one"]
