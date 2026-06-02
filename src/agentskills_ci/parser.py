from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
CODE_PATH_RE = re.compile(r"`([^`]+)`")
LINK_PATH_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ALLOWED_LINK_PREFIXES = ("references/", "templates/", "scripts/", "assets/")


@dataclass(frozen=True)
class Skill:
    """Parsed representation of a single SKILL.md file."""

    path: Path
    root: Path
    frontmatter: dict[str, Any]
    body: str
    referenced_paths: list[Path]

    @property
    def name(self) -> str:
        return str(self.frontmatter.get("name") or self.path.parent.name)

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description") or "")


def parse_skill_file(path: str | Path) -> Skill:
    """Parse a SKILL.md file into frontmatter, body, and local skill-file references."""

    skill_path = Path(path)
    content = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        # Keep parsing failures as a Skill so validators can produce friendly output.
        return Skill(path=skill_path, root=skill_path.parent, frontmatter={}, body=content, referenced_paths=[])

    frontmatter_text, body = match.groups()
    loaded = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(loaded, dict):
        loaded = {}

    references = _extract_referenced_paths(body)
    return Skill(path=skill_path, root=skill_path.parent, frontmatter=loaded, body=body, referenced_paths=references)


def discover_skill_files(path: str | Path) -> list[Path]:
    """Return all SKILL.md files under a directory, sorted for stable CI output."""

    root = Path(path)
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("SKILL.md") if p.is_file())


def _extract_referenced_paths(markdown: str) -> list[Path]:
    found: list[Path] = []
    candidates = [m.group(1).strip() for m in CODE_PATH_RE.finditer(markdown)]
    candidates.extend(m.group(1).strip() for m in LINK_PATH_RE.finditer(markdown))

    for raw in candidates:
        if raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Strip optional line anchors/fragments.
        clean = raw.split("#", 1)[0]
        if not clean:
            continue
        if clean.startswith(ALLOWED_LINK_PREFIXES):
            path = Path(clean)
            if path not in found:
                found.append(path)
    return found
