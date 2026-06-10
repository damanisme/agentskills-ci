from __future__ import annotations

import argparse
import sys
from pathlib import Path

import json

from .badge import build_endpoint, build_markdown, build_url
from .parser import discover_skill_files, parse_skill_file
from .report import render_json, render_markdown, render_text, summarize
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
    check.add_argument("-o", "--output", default=None, help="Write the report to this file (UTF-8) instead of stdout")

    score = subparsers.add_parser("score", help="Alias for check that prints reports")
    score.add_argument("path", help="Skill directory or SKILL.md file")
    score.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    score.add_argument("--min-score", type=int, default=0, help="Minimum per-skill passing score")
    score.add_argument("-o", "--output", default=None, help="Write the report to this file (UTF-8) instead of stdout")

    init = subparsers.add_parser("init-github-action", help="Create .github workflow for agentskills-ci")
    init.add_argument("--repo", default=".", help="Repository root where workflow should be written")
    init.add_argument("--path", default="skills", help="Skill path to validate in CI")

    badge = subparsers.add_parser("badge", help="Emit a shields.io quality badge for a skill path")
    badge.add_argument("path", help="Skill directory or SKILL.md file")
    badge.add_argument("--format", choices=("markdown", "url", "endpoint"), default="markdown")
    badge.add_argument("--label", default="skill score", help="Badge left-side label")
    badge.add_argument("--repo", default=None, help="Repo URL to link the markdown badge back to")
    return parser


def _force_utf8_output() -> None:
    """Ensure stdout/stderr can emit non-ASCII (emoji in reports).

    On Windows the default console encoding is often a legacy code page such as
    cp1252, which raises UnicodeEncodeError on characters like the status icons.
    Reconfiguring to UTF-8 with replacement keeps output working everywhere.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8_output()
    args = build_parser().parse_args(argv)
    if args.command in {"check", "score"}:
        return _run_check(Path(args.path), args.format, args.min_score, args.output)
    if args.command == "init-github-action":
        return _init_github_action(Path(args.repo), args.path)
    if args.command == "badge":
        return _run_badge(Path(args.path), args.format, args.label, args.repo)
    raise AssertionError(f"Unhandled command: {args.command}")


def _run_check(path: Path, output_format: str, min_score: int, output: str | None = None) -> int:
    files = discover_skill_files(path)
    if not files:
        print(f"No SKILL.md files found under {path}", file=sys.stderr)
        return 2

    results = [validate_skill(parse_skill_file(file)) for file in files]
    if output_format == "json":
        report = render_json(results, min_score)
    elif output_format == "markdown":
        report = render_markdown(results, min_score) + "\n"
    else:
        report = render_text(results, min_score)

    if output:
        Path(output).write_text(report, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(report, end="")

    failed = [result for result in results if not result.passes(min_score)]
    return 1 if failed else 0


def _run_badge(path: Path, output_format: str, label: str, repo: str | None) -> int:
    files = discover_skill_files(path)
    if not files:
        print(f"No SKILL.md files found under {path}", file=sys.stderr)
        return 2

    results = [validate_skill(parse_skill_file(file)) for file in files]
    score = summarize(results)["overall_score"]

    if output_format == "endpoint":
        print(json.dumps(build_endpoint(score, label), indent=2))
    elif output_format == "url":
        print(build_url(score, label))
    else:
        print(build_markdown(score, label, repo))
    return 0


def _init_github_action(repo: Path, path: str) -> int:
    workflow = repo / ".github" / "workflows" / "agentskills-ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(WORKFLOW_TEMPLATE.format(path=path), encoding="utf-8")
    print(f"Wrote {workflow}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
