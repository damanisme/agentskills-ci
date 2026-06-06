---
name: fixed-skill
description: Use when you need the remediated twin of bad-skill that demonstrates how every agentskills-ci penalty is resolved to reach a perfect score.
version: 1.0.0
author: agentskills-ci
license: MIT
metadata:
  hermes:
    tags: [example, skills, ci, remediation]
    related_skills: []
---

# Fixed Skill

## Overview

This skill is the corrected version of `bad-skill`. It keeps the same intent but
removes every issue the scorer flags: missing description, missing sections, a
dead file reference, a risky command, and an ungated side effect.

## When to Use

- When showing how to lift a failing skill from a low score to 100.
- When copying a known-good remediation pattern for a new agent skill.

## Workflow

1. Clean up a temporary demo directory using the safe helper in `scripts/cleanup.sh`.
2. Draft the social post, but ask the user for explicit approval before posting to Twitter.
3. Verify each checklist item before responding.

## Common Pitfalls

1. Leaving a recursive force-delete command in the body instead of a scoped, reviewed helper script.
2. Referencing helper files such as `scripts/cleanup.sh` that do not exist on disk.
3. Performing a side effect (posting, deploying) without an approval gate.

## Verification Checklist

- [ ] Frontmatter includes name and description.
- [ ] Referenced files exist.
- [ ] Commands are safe and any side effect waits for user approval.
