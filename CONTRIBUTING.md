# Contributing to agentskills-ci

Thanks for your interest! This is a young project and contributions — bug
reports, new validation rules, docs — are all welcome.

## Development setup

```bash
git clone https://github.com/damanisme/agentskills-ci
cd agentskills-ci
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Before opening a PR

Run the same checks CI runs:

```bash
ruff check src tests
pytest -q
```

Both must pass. CI runs them on Python 3.9, 3.11, and 3.12.

## Project layout

| Path | Purpose |
| --- | --- |
| `src/agentskills_ci/parser.py` | Discover and parse `SKILL.md` files |
| `src/agentskills_ci/validators.py` | Rules + scoring (the heart of the tool) |
| `src/agentskills_ci/report.py` | text / Markdown / JSON output |
| `src/agentskills_ci/badge.py` | shields.io quality badge |
| `src/agentskills_ci/cli.py` | command-line entry point |
| `examples/skills/` | `good-skill` / `fixed-skill` (100), `bad-skill` (failing fixture) |

## Adding or changing a validation rule

Rules live in `validators.py`. Each issue is an `Issue(severity, message, penalty)`
subtracted from a starting score of 100.

1. Add the rule in the relevant `_validate_*` function (or a new one wired into
   `validate_skill`).
2. **Write a test first** in `tests/test_validators.py` — cover both a skill that
   triggers the rule and one that does not. Watch out for false positives (a
   skill that *warns against* `rm -rf` should not be flagged like one that runs
   it).
3. Keep severities meaningful: `error` blocks the gate, `warning`/`info` only
   lower the score.
4. Update `README.md` ("What gets checked") and `CHANGELOG.md`.

## Pull requests

- Branch off `main`; keep PRs focused.
- Reference any related issue.
- Describe what you changed and how you verified it.
- Squash-merge is used; a clean, conventional commit subject is appreciated
  (`fix:`, `feat:`, `docs:`, `ci:`).

## Releases

Maintainers only — see [`PUBLISHING.md`](PUBLISHING.md).

## Reporting bugs

Open an issue with the `SKILL.md` (or a minimal reproduction), the command you
ran, and the output you got versus what you expected.
