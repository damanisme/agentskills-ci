---
name: good-skill
description: Use when demonstrating a high-quality Claude/Hermes AI-agent skill with CI-friendly structure.
version: 1.0.0
author: agentskills-ci
license: MIT
metadata:
  hermes:
    tags: [example, skills, ci]
    related_skills: []
---

# Good Skill

## Overview

This example shows a skill with clear trigger conditions, operational guidance, safety boundaries, linked references, common pitfalls, and verification steps.

## When to Use

- When testing agentskills-ci against a known-good example
- When copying a starter structure for a new agent skill

## Workflow

1. Read the user's task and determine whether this skill applies.
2. Follow the workflow in `references/guide.md`.
3. Verify the output before responding.

## Common Pitfalls

1. Writing vague trigger descriptions that activate for too many tasks.
2. Referencing helper files that do not exist.
3. Adding side-effect actions without explicit approval gates.

## Verification Checklist

- [ ] Frontmatter includes name and description.
- [ ] Referenced files exist.
- [ ] Commands are safe or clearly gated.
