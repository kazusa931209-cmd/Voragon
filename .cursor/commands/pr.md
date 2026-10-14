
# Pull request (title & description)

Generate a **copy-paste-ready** GitHub PR title and description for the current branch. Do **not** push or run `gh pr create` unless the user explicitly asks to open the PR.

## Steps

1. Run in parallel:
   - `git branch --show-current`
   - `git status --short`
   - `git remote show origin` (or `git rev-parse --abbrev-ref @{upstream}`) to see tracking / default branch if available
2. Determine the **base branch** (usually `main` or `master`). If unclear, use `main` and note the assumption.
3. Run `git log --oneline <base>...HEAD` and `git diff <base>...HEAD --stat` to list commits and scope on this branch.
4. Map commits to dev-steps:
   - Prefer subjects like `[P2-006] …` in commit messages.
   - Read linked docs under `docs/roadmap/dev-step-*.md` for each step in the PR (scope, manual test, completion / spec changes, test commands).
5. Draft:
   - **Title:** concise, matches dev-step naming when the PR is a single step (e.g. `[P2-006] session.resume reconnection`). For multiple dev-step commits, use a summary title and list steps in the body.
   - **Description:** use the Voragon optional PR body from `.cursor/rules/dev-workflow.mdc`:
     - `## Dev-step` (id, title, doc path — one block per step if several)
     - `## Spec` (docs changed, or "none")
     - `## Manual test` (unchecked checklist from dev-step doc(s))
     - `## Automated tests` (commands + result from completion section, or suggest commands to run)
   - Add a short **Summary** (2–4 bullets) at the top if it helps reviewers and is not redundant with Dev-step.
6. Present output **only** in two fenced code blocks so the user can copy each in one click:

   First block — label: **PR title (copy)**

   ```text
   <single line title, no markdown heading>
   ```

   Second block — label: **PR description (copy)**

   ```markdown
   <full body>
   ```

7. After the blocks, briefly note: base branch used, commit count, and any unstaged/unpushed caveats (e.g. local commits not pushed yet).

## Approval

- Do **not** push, `gh pr create`, or change git state.
- If the branch has no commits ahead of base, say so and still offer a draft title/body only if useful (e.g. for an empty PR template).
- Do **not** read secrets or `.env` files.

## Optional: open PR

If the user says to **create** or **open** the PR (not just `/pr`):

1. Follow the user’s pull-request workflow (push with `-u` if needed, then `gh pr create` with `--title` and `--body` from the approved draft).

## Constraints

- Use repository facts from git and dev-step docs; do not invent merged PR links or test results.
- Keep the description proportional; prefer checklists and paths over long prose.
