"""agentskills-ci: CI-quality validation for AI-agent skills."""

from .parser import Skill, discover_skill_files, parse_skill_file
from .validators import Issue, ValidationResult, validate_skill

__all__ = [
    "Issue",
    "Skill",
    "ValidationResult",
    "discover_skill_files",
    "parse_skill_file",
    "validate_skill",
]

__version__ = "0.1.0"
