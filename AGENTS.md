# Dungeon Game project instructions

## Start every task

- Read `docs/knowledge/README.md` before making project changes.
- Follow only the knowledge-base links relevant to the task.
- Treat Roblox Studio place **Dungeon Game** (`placeId: 118646628582446`) as the intended live project. If more than one Studio instance is connected, confirm the target before changing it.
- Preserve unrelated user changes in both the repository and Studio.

## Keep project memory current

After material work, update project memory in the same change:

- Update `docs/knowledge/project.md` when current structure, systems, conventions, or dependencies change.
- Add an entry to `docs/knowledge/decisions.md` for a durable technical or product choice. Supersede accepted historical decisions instead of rewriting them.
- Add a concise entry to `docs/knowledge/work-log.md` for completed work, including verification and important paths.
- Update `docs/knowledge/asset-catalog.md` when assets are added, renamed, replaced, or removed.
- Update or add a skill under `.agents/skills/` only when work establishes a reusable workflow or non-obvious project rule.
- Never record secrets, tokens, private credentials, or speculative claims in project memory.

Documentation-only exploration does not require a work-log entry. If a task makes no durable change, do not manufacture an update.

## Roblox Studio workflow

- Inspect the current Studio state before edits.
- Prefer targeted edits and inspect affected instances afterward.
- Playtest gameplay or UI behavior changes in the appropriate DataModel and review Studio console output before declaring success.
- Stop play mode when verification is complete unless the user asks to leave it running.

## Git and GitHub workflow

- Keep repository knowledge, skills, source, and project-owned assets in Git.
- Never commit credentials, generated caches, temporary captures, or local Studio state.
- Before a commit or pull request, review `git diff`, run relevant validation, and summarize verification.
- Do not push, create a remote repository, publish a place, or open a pull request unless the user authorizes that external action.

## Code review rules

- Flag changes that alter live Studio behavior without corresponding verification evidence.
- Flag material project changes that leave the relevant knowledge file stale.
- Flag hard-coded secrets, credentials, or machine-specific absolute paths.
