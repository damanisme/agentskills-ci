# Publishing to PyPI

`agentskills-ci` publishes via **PyPI Trusted Publishing (OIDC)** — GitHub
Actions authenticates to PyPI with a short-lived token. **No password or API
token is ever stored** in the repo, in `.env`, or anywhere else.

The release workflow is `.github/workflows/release.yml`; it runs on a published
GitHub Release.

## One-time setup

These steps are interactive and can only be done by a human (email verification,
CAPTCHA, and 2FA cannot be automated).

1. **Register a PyPI account** — https://pypi.org/account/register/
   - Verify the confirmation email.
   - Store the password in a password manager (never in `.env`).
2. **Enable 2FA** — PyPI requires it before you can publish.
   Account settings → Two-factor authentication.
3. **Add a pending publisher** — https://pypi.org/manage/account/publishing/
   Under "Add a pending publisher" (GitHub tab), fill in exactly:

   | Field | Value |
   | --- | --- |
   | PyPI Project Name | `agentskills-ci` |
   | Owner | `damanisme` |
   | Repository name | `agentskills-ci` |
   | Workflow name | `release.yml` |
   | Environment name | *(leave blank)* |

   It is called "pending" because the project does not exist on PyPI yet; the
   first successful publish creates it.

   > The Environment field **must be blank** — `release.yml` does not declare a
   > GitHub Environment, so the OIDC claims carry no `environment`. A publisher
   > configured with an environment will fail to match (`invalid-publisher`).

## Cutting a release

1. Bump `version` in `pyproject.toml` if needed and update `CHANGELOG.md`.
2. Create a GitHub Release whose tag matches the version, e.g. `v0.1.0`:

   ```bash
   gh release create v0.1.0 --target main --title "v0.1.0" \
     --notes-file .github/RELEASE_NOTES_v0.1.0.md
   ```

3. Publishing the release triggers `release.yml`, which builds the sdist + wheel
   and uploads them to PyPI via trusted publishing.

## Verifying

```bash
pip index versions agentskills-ci   # should list the new version
pipx install agentskills-ci
```

## Troubleshooting

- **`invalid-publisher`: no corresponding publisher** — the pending publisher is
  missing or its fields do not match the workflow's OIDC claims. Re-check the
  table above; the most common mismatch is a non-blank Environment field. The
  failed run's log prints the exact claims (`repository`, `workflow_ref`,
  `environment`) for comparison.
- The workflow runs from the **tag**, not `main`. If you change `release.yml`,
  re-cut the tag so the release runs the updated workflow.
- After fixing the publisher, no re-cut is needed — re-run the failed job:
  `gh run rerun <run-id>`.
