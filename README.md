# agentskills-ci

[![CI](https://github.com/damanisme/agentskills-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/damanisme/agentskills-ci/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agentskills-ci)](https://pypi.org/project/agentskills-ci/)
[![Python versions](https://img.shields.io/pypi/pyversions/agentskills-ci)](https://pypi.org/project/agentskills-ci/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![skill score](https://img.shields.io/badge/skill%20score-100-brightgreen)

> **Test, lint, score, and package Claude/Hermes/AI-agent skills like real software.**

Claude Skills and agent workflows are becoming reusable software artifacts, but most teams still ship them as loose prompt files. No CI. No tests. No linked-file checks. No safety scan. No quality score.

`agentskills-ci` gives AI-agent skills the same quality discipline teams expect from code.

## Demo

Score a whole skills directory in one command — pass on the good, fail on the dangerous:

```console
$ agentskills-ci score ./skills

⚠️ 3 skills checked
✅ 2 passed
⚠️  1 need fixes

Overall score: 68/100

Top issues:
- bad-skill: Risky command pattern found: rm -rf
- bad-skill: Side-effect instruction lacks an approval gate
- bad-skill: Referenced path does not exist: scripts/missing.sh
```

```console
$ agentskills-ci badge ./skills --repo https://github.com/you/your-repo
[![skill score](https://img.shields.io/badge/skill%20score-100-brightgreen)](https://github.com/you/your-repo)
```

<!-- To record a GIF for this section:
     asciinema rec demo.cast -c "agentskills-ci score ./skills"
     agg demo.cast docs/demo.gif   # then embed: ![demo](docs/demo.gif) -->

## What it does

- Validates `SKILL.md` frontmatter and body structure
- Checks for missing linked files in `references/`, `templates/`, `scripts/`, and `assets/`
- Flags risky shell patterns such as `rm -rf`, `curl | bash`, and broad permission changes
- Flags external side-effect instructions without approval gates
- Scores each skill from `0–100`
- Emits text, Markdown, or JSON reports
- Provides a composite GitHub Action via `action.yml`
- Includes a workflow generator: `agentskills-ci init-github-action`

## Quick start

```bash
pipx install agentskills-ci
agentskills-ci check ./skills
agentskills-ci score ./skills --format markdown
agentskills-ci init-github-action --path skills
```

Local development from this repo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
agentskills-ci check examples/skills/good-skill
```

## Example output

```text
✅ 1 skills checked
✅ 1 passed
⚠️  0 need fixes

Overall score: 100/100
```

Bad-skill example:

```text
⚠️  1 skills checked
✅ 0 passed
⚠️  1 need fixes

Overall score: 8/100

Top issues:
- bad-skill: Missing required frontmatter field: description
- bad-skill: Missing recommended section: ## Overview
- bad-skill: Referenced path does not exist: scripts/missing.sh
- bad-skill: Risky command pattern found: rm -rf
- bad-skill: Side-effect instruction lacks an approval gate
```

## GitHub Action usage

Use the published action from a workflow in another repository:

```yaml
name: Agent Skills CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: damanisme/agentskills-ci@main
        with:
          path: skills
          min-score: "80"
          format: text
```

Or generate a workflow locally:

```bash
agentskills-ci init-github-action --repo . --path skills
```

A sample workflow is included at `examples/github-workflows/ci.yml`.

## CLI

```bash
agentskills-ci check PATH [--format text|markdown|json] [--min-score 80] [-o FILE]
agentskills-ci score PATH [--format text|markdown|json] [-o FILE]
agentskills-ci init-github-action [--repo .] [--path skills]
agentskills-ci badge PATH [--format markdown|url|endpoint] [--label "skill score"] [--repo URL]
```

### Quality badge

Show your skill score in any README. Generate a static badge:

```bash
agentskills-ci badge ./skills --repo https://github.com/you/your-repo
# [![skill score](https://img.shields.io/badge/skill%20score-100-brightgreen)](https://github.com/you/your-repo)
```

Or wire a live, self-updating badge via a shields.io endpoint. Publish the JSON
from `agentskills-ci badge ./skills --format endpoint` to a URL, then point
shields.io at it:

```md
![skill score](https://img.shields.io/endpoint?url=https://your-host/skill-score.json)
```

Badge color tracks the score: `>=90` brightgreen, `>=80` green, `>=60` yellow,
`>=40` orange, else red.

`PATH` can be either a single `SKILL.md` file or a directory containing nested skill folders. Symlinked skill directories are followed (with cycle protection), so an aggregated `skills/` folder that links skills in from elsewhere is fully scanned.

## What gets checked

### Required structure

- YAML frontmatter starts at the top of `SKILL.md`
- Required fields: `name`, `description`
- Description length <= 1024 characters
- Skill name is lowercase and URL-safe

### Recommended sections

- `## Overview`
- `## When to Use`
- `## Common Pitfalls`
- `## Verification Checklist`

### Linked files

References to these folders are validated:

- `references/`
- `templates/`
- `scripts/`
- `assets/`

Example:

```md
See `references/api.md` and `scripts/check.sh`.
```

If either file is missing, CI fails.

### Safety scan

Current MVP rules flag:

- `rm -rf`
- `curl | bash`
- `chmod 777`
- suspicious secret literals
- destructive `sudo` commands
- side-effect actions such as posting, deploying, sending email, or merging without an approval gate

## Why this matters

Agent skills are operational runbooks. A bad skill can:

- trigger at the wrong time
- reference missing support files
- tell an agent to run dangerous commands
- perform external side effects without approval
- silently drift out of date

`agentskills-ci` makes these problems visible in pull requests.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the full list. Highlights:

- SARIF output for GitHub code scanning
- ✅ Badge endpoint / static badge generation (`agentskills-ci badge`)
- Skill registry quality cards
- LLM-assisted skill critique mode
- Overlap detection between related skills
- Policy packs for enterprise teams
- Test fixtures for tool-call simulations
- Package publishing to PyPI

## Repository structure

```text
agentskills-ci/
├── action.yml
├── examples/
│   ├── github-workflows/
│   └── skills/
├── src/agentskills_ci/
├── templates/
├── tests/
└── pyproject.toml
```

## License

MIT
