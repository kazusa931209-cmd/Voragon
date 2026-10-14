
# Commit

Prepare a Git commit for the current repository.

## Steps

1. Run `git status --short` and note the current branch.
2. Review staged changes with `git diff --cached`.
3. Review unstaged changes with `git diff`.
4. Inspect untracked files as needed, but do **not** read secrets, credentials, or environment files (e.g. `.env`).
5. Draft a concise commit message based on the actual diff.
6. Present the proposed message to the user before committing.

## Approval

- Do **not** commit until the user explicitly approves the proposed message.
- Do **not** stage all files automatically.
- If there are unstaged or untracked changes, explain what they contain and ask which files to stage.
- Do **not** overwrite, discard, or reset the user’s changes.
- Do **not** amend the previous commit unless the user explicitly asks.
- Do **not** skip hooks or tests (no `--no-verify`, etc.).

## After approval

1. Stage only the files the user approved.
2. Commit with the approved message.
3. Run `git status --short` and `git log -1 --format='%h %an <%ae> %s'`.
4. Report the commit hash, message, author, and any errors.

## Constraints

- Use the repository’s existing local Git identity (`user.name` / `user.email`). Do not change Git config or GitHub authentication.
- Do not push or open a pull request as part of this command.
