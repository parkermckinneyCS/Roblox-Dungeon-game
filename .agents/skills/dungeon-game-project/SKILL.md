---
name: dungeon-game-project
description: Work on the Dungeon Game Roblox project using its living knowledge base, Studio identity, asset conventions, decision history, and post-change documentation workflow. Use for implementation, debugging, UI or asset work, architecture decisions, and project status questions in this repository.
---

# Dungeon Game project workflow

Start with `docs/knowledge/README.md` and read only the linked sections relevant to the request.

Before changing Roblox Studio, list connected Studio instances and select **Dungeon Game** (`placeId: 118646628582446`). Inspect its mode and the target hierarchy before editing. If multiple plausible instances exist, ask which one to use before mutation.

Preserve the boundary between facts and plans:

- Record verified current behavior and structure in `docs/knowledge/project.md`.
- Record durable choices with context and consequences in `docs/knowledge/decisions.md`.
- Record completed material work and verification in `docs/knowledge/work-log.md`.
- Keep `docs/knowledge/asset-catalog.md` synchronized with asset changes.
- Keep future ideas and unresolved work in `docs/knowledge/backlog.md`; do not describe them as implemented.

After material work, update the smallest relevant knowledge files in the same change. Add or revise repository skills only when the work reveals a reusable procedure or non-obvious rule. Never store secrets, credentials, or guesses as project knowledge.

For Studio changes, verify affected instances and relevant output. Playtest behavior changes in the appropriate DataModel, inspect console output, and return to Edit mode when finished unless asked otherwise.
