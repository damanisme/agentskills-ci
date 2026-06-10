# Changelog

All notable changes to `agentskills-ci` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-06-09

### Added
- `score` and `check` accept `-o/--output FILE` to write the report to a file as
  UTF-8 (instead of stdout). Avoids the Windows `>` redirect writing UTF-16 and
  mangling the status icons.

## [0.1.1] - 2026-06-09

### Fixed
- Windows: `score`/`check` text output no longer crashes with
  `UnicodeEncodeError` on consoles using a legacy code page (e.g. cp1252). The
  CLI now reconfigures stdout/stderr to UTF-8. Found by installing the published
  package into a clean Windows venv and running it. (regression test added)

## [Unreleased]

Work from 2026-06-06.

### Added
- `agentskills-ci badge` command — emit a shields.io quality badge for any skill
  path in `markdown`, `url`, or `endpoint` (live, self-updating) format. Badge
  color tracks score: `>=90` brightgreen, `>=80` green, `>=60` yellow, `>=40`
  orange, else red. (`src/agentskills_ci/badge.py`, PR #1)
- `examples/skills/fixed-skill` — a verified 100/100 remediated twin of
  `bad-skill`, with a safe, approval-gated cleanup script. `bad-skill` is kept
  intact as the deliberate failing fixture. (PR #1)
- Self-badge and a "Quality badge" section in the README. (PR #1)
- `ROADMAP.md` — public, forward-looking roadmap.
- CI workflow (`.github/workflows/ci.yml`) running ruff + pytest on Python
  3.9/3.11/3.12 plus a self-score of the example skills. *(staged; pending a
  token with `workflow` scope to push)*
- PyPI release workflow (`.github/workflows/release.yml`) using Trusted
  Publishing (OIDC, no stored token), triggered on a GitHub Release. *(staged;
  pending `workflow` scope + a one-time PyPI pending-publisher setup)*

### Changed
- README roadmap now links to `ROADMAP.md` instead of duplicating the list.

### Fixed
- `discover_skill_files` now follows directory symlinks (with realpath cycle
  protection and de-duplication). An aggregated `skills/` folder that links
  skills in from elsewhere is fully scanned instead of silently under-counted —
  found while dogfooding the CLI against a real corpus where 6 of 22 skills
  were being skipped. (PR #2)

### Removed
- `docs/CLAUDE_CODE_REVIEW_2026-06-02.md` — an internal self-critique with stale
  findings (approval-gate and `--min-score` already fixed; score badge now
  shipped), a session id, and career framing not meant for public repo visitors.

### Verification
- `pytest -q` → 19 passed. `ruff check src tests` → clean.
- `python -m build` + `twine check dist/*` → PASSED. Name `agentskills-ci` is
  available on PyPI.
- CLI dogfooded against a real skill corpus: 22/22 skills discovered after the
  symlink fix (was 6).
