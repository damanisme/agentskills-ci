# Roadmap

Planned work for `agentskills-ci`, roughly in priority order. Done items live in
the changelog / git history, not here.

## Adoption & integration

- **GitHub PR annotations** — emit `::error file=...,line=...::` workflow
  commands so findings render inline on pull requests.
- **SARIF output** — enable GitHub code scanning integration.
- **PyPI publishing** — ship `0.1.0` so the `pipx install agentskills-ci`
  quick-start works for real users.
- **Self-CI workflow** — add `.github/workflows/ci.yml` (run lint + tests on PRs)
  and a CI status badge. Requires a token with `workflow` scope.

## Detection quality

- Reduce safety-scan false positives — a skill warning *against* a dangerous
  command should not score the same as one instructing it.
- Expand risky-shell detection beyond `curl | bash` to `curl | sh`,
  `curl | zsh`, and similar variants.
- Overlap detection between related skills.
- Policy packs for enterprise teams.

## Ecosystem

- Explicit Claude Skills convention support (match Anthropic/Claude skill
  conventions by name).
- Skill registry quality cards.
- LLM-assisted skill critique mode.
- Test fixtures for tool-call simulations.

## Project hygiene

- Add `--version`, `CONTRIBUTING.md`, and `CHANGELOG.md`.
- Keep public identity consistent across `pyproject.toml`, `action.yml`,
  README, and the GitHub username.
