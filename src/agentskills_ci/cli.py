from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import discover_skill_files, parse_skill_file
from .report import render_json, render_markdown, render_text
from .validators import validate_skill

WORKFLOW_TEMPLATE = """name: Agent Skills CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install agentskills-ci
        run: pip install agentskills-ci
      - name: Validate skills
        run: agentskills-ci check {path}
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentskills-ci",
        description="Validate, score, and report on Claude/Hermes/AI-agent skills.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Validate skills and fail on low-quality results")
    check.add_argument("path", help="Skill directory or SKILL.md file")
    check.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    check.add_argument("--min-score", type=int, default=80, help="Minimum per-skill passing score")

    score = subparsers.add_parser("score", help="Alias for check that prints reports")
    score.add_argument("path", help="Skill directory or SKILL.md file")
    score.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    score.add_argument("--min-score", type=int, default=0, help="Minimum per-skill passing score")

    init = subparsers.add_parser("init-github-action", help="Create .github workflow for agentskills-ci")
    init.add_argument("--repo", default=".", help="Repository root where workflow should be written")
    init.add_argument("--path", default="skills", help="Skill path to validate in CI")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in {"check", "score"}:
        return _run_check(Path(args.path), args.format, args.min_score)
    if args.command == "init-github-action":
        return _init_github_action(Path(args.repo), args.path)
    raise AssertionError(f"Unhandled command: {args.command}")


def _run_check(path: Path, output_format: str, min_score: int) -> int:
    files = discover_skill_files(path)
    if not files:
        print(f"No SKILL.md files found under {path}", file=sys.stderr)
        return 2

    results = [validate_skill(parse_skill_file(file)) for file in files]
    if output_format == "json":
        print(render_json(results), end="")
    elif output_format == "markdown":
        print(render_markdown(results))
    else:
        print(render_text(results), end="")

    failed = [result for result in results if result.score < min_score or not result.passed]
    return 1 if failed else 0


def _init_github_action(repo: Path, path: str) -> int:
    workflow = repo / ".github" / "workflows" / "agentskills-ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(WORKFLOW_TEMPLATE.format(path=path), encoding="utf-8")
    print(f"Wrote {workflow}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
