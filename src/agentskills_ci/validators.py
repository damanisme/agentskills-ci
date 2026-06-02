from __future__ import annotations

import re
from dataclasses import dataclass, field
from .parser import Skill

REQUIRED_FRONTMATTER = ("name", "description")
RECOMMENDED_SECTIONS = (
    "## Overview",
    "## When to Use",
    "## Common Pitfalls",
    "## Verification Checklist",
)
RISKY_PATTERNS = (
    ("rm -rf", re.compile(r"\brm\s+-rf\b")),
    ("curl | bash", re.compile(r"curl\b[^`\n|]*\|\s*(?:sudo\s+)?bash")),
    ("chmod 777", re.compile(r"\bchmod\s+777\b")),
    ("sudo destructive command", re.compile(r"\bsudo\s+(?:rm|dd|mkfs|shutdown|reboot)\b")),
    ("secret literal", re.compile(r"(?i)(api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_\-]{16,}")),
)
SIDE_EFFECT_PATTERNS = (
    re.compile(r"\bsend\s+email\b", re.IGNORECASE),
    re.compile(r"\bpost\s+to\s+twitter\b", re.IGNORECASE),
    re.compile(r"\btweet\b", re.IGNORECASE),
    re.compile(r"\bdeploy\b", re.IGNORECASE),
    re.compile(r"\bpublish\b", re.IGNORECASE),
    re.compile(r"\bcharge\s+card\b", re.IGNORECASE),
    re.compile(r"\bdelete\s+production\b", re.IGNORECASE),
    re.compile(r"\bmerge\s+the\s+pr\b", re.IGNORECASE),
)
APPROVAL_PATTERNS = (
    re.compile(r"\bask\b", re.IGNORECASE),
    re.compile(r"\bconfirm\b", re.IGNORECASE),
    re.compile(r"\bapproval\b", re.IGNORECASE),
    re.compile(r"\bexplicit\s+permission\b", re.IGNORECASE),
    re.compile(r"\buser\s+approves\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class Issue:
    severity: str
    message: str
    penalty: int
    path: str | None = None


@dataclass
class ValidationResult:
    skill: Skill
    score: int
    issues: list[Issue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.passes()

    def passes(self, min_score: int = 80) -> bool:
        return self.score >= min_score and not any(issue.severity == "error" for issue in self.issues)

    def to_dict(self, min_score: int = 80) -> dict:
        return {
            "name": self.skill.name,
            "path": str(self.skill.path),
            "score": self.score,
            "passed": self.passes(min_score),
            "issues": [issue.__dict__ for issue in self.issues],
        }


def validate_skill(skill: Skill) -> ValidationResult:
    """Validate one parsed skill and return a weighted quality score."""

    issues: list[Issue] = []
    _validate_frontmatter(skill, issues)
    _validate_sections(skill, issues)
    _validate_links(skill, issues)
    _validate_security(skill, issues)
    _validate_activation_quality(skill, issues)

    score = max(0, 100 - sum(issue.penalty for issue in issues))
    return ValidationResult(skill=skill, score=score, issues=issues)


def _validate_frontmatter(skill: Skill, issues: list[Issue]) -> None:
    content = skill.path.read_text(encoding="utf-8") if skill.path.exists() else ""
    if not content.startswith("---"):
        issues.append(Issue("error", "SKILL.md must start with YAML frontmatter", 25))
    for field_name in REQUIRED_FRONTMATTER:
        if field_name not in skill.frontmatter or not skill.frontmatter.get(field_name):
            issues.append(Issue("error", f"Missing required frontmatter field: {field_name}", 25))
    description = str(skill.frontmatter.get("description") or "")
    if len(description) > 1024:
        issues.append(Issue("error", "Description exceeds 1024 characters", 15))
    name = str(skill.frontmatter.get("name") or "")
    if name and not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name):
        issues.append(Issue("warning", "Skill name should be lowercase, URL-safe, and <=64 chars", 8))


def _validate_sections(skill: Skill, issues: list[Issue]) -> None:
    body_lower = skill.body.lower()
    for section in RECOMMENDED_SECTIONS:
        if section.lower() not in body_lower:
            issues.append(Issue("warning", f"Missing recommended section: {section}", 5))


def _validate_links(skill: Skill, issues: list[Issue]) -> None:
    for relative_path in skill.referenced_paths:
        if relative_path.is_absolute() or ".." in relative_path.parts:
            issues.append(Issue("error", f"Unsafe referenced path: {relative_path.as_posix()}", 15, relative_path.as_posix()))
            continue
        if not (skill.root / relative_path).exists():
            issues.append(
                Issue(
                    "error",
                    f"Referenced path does not exist: {relative_path.as_posix()}",
                    15,
                    relative_path.as_posix(),
                )
            )


def _validate_security(skill: Skill, issues: list[Issue]) -> None:
    combined = f"{skill.description}\n{skill.body}"
    for label, pattern in RISKY_PATTERNS:
        if pattern.search(combined):
            issues.append(Issue("error", f"Risky command pattern found: {label}", 20))

    has_side_effect = any(pattern.search(combined) for pattern in SIDE_EFFECT_PATTERNS)
    has_approval_gate = any(pattern.search(combined) for pattern in APPROVAL_PATTERNS)
    if has_side_effect and not has_approval_gate:
        issues.append(Issue("warning", "Side-effect instruction lacks an approval gate", 12))


def _validate_activation_quality(skill: Skill, issues: list[Issue]) -> None:
    description = skill.description.strip()
    if description and not description.lower().startswith(("use when", "when to use", "trigger")):
        issues.append(Issue("info", "Description should start with a clear trigger such as 'Use when ...'", 4))
    if len(skill.body.strip()) < 80:
        issues.append(Issue("warning", "Skill body is very short; add actionable workflow detail", 10))
    if "- [ ]" not in skill.body and "- [x]" not in skill.body:
        issues.append(Issue("info", "Verification checklist should include checkbox items", 3))
