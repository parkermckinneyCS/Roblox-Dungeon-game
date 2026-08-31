# Dungeon Game technical knowledge base

This directory is the persistent architecture reference for the live Roblox place **Dungeon Game** (`placeId: 118646628582446`). Future agents should read this page and the relevant linked documents before changing Studio.

Last full Studio architecture audit: **2026-08-28**

The audit was performed through Roblox Studio MCP against the Edit DataModel. It was static and read-only: the game was not started, scripts were not executed, and no Studio instances or properties were changed.

## Reading order

| Document | Contents |
| --- | --- |
| [`project-prompt.md`](project-prompt.md) | Reusable Codex prompt and the idea-to-documentation lifecycle |
| [`architecture.md`](architecture.md) | System boundaries, lifecycle, dependencies, and data ownership |
| [`networking.md`](networking.md) | All project RemoteEvents, RemoteFunctions, bindables, callers, and handlers |
| [`instance-paths.md`](instance-paths.md) | Important live Studio paths and runtime-created instances |
| [`conventions.md`](conventions.md) | Naming and schema contracts that implementations must preserve |
| [`known-problems.md`](known-problems.md) | Verified defects, security risks, design gaps, and follow-up validation |
| [`knowledge/README.md`](knowledge/README.md) | Decisions, asset catalog, GitHub state, backlog, and work history |

## Source-of-truth boundaries

- The live Studio place is currently the source of truth for Luau scripts and the DataModel hierarchy.
- This repository does **not** currently contain a Rojo project or a checked-in mirror of the Studio scripts. Git therefore preserves these documents and local assets, but not the complete live game implementation.
- `docs/architecture.md`, `docs/networking.md`, and `docs/instance-paths.md` describe verified current behavior.
- `docs/known-problems.md` distinguishes observed defects from design gaps and runtime questions.
- `docs/knowledge/decisions.md` is the durable decision history; do not rewrite accepted decisions to match later preferences.

## Future-agent checklist

1. Read `docs/knowledge/README.md`, this index, and the documents relevant to the task.
2. List connected Studio instances and select **Dungeon Game** with place ID `118646628582446`.
3. Confirm the Studio mode and re-inspect every path that will be changed; the live place may have moved ahead of this snapshot.
4. Preserve the server-authoritative remote boundary and the identifier/path contracts in `conventions.md`.
5. After material changes, update the smallest affected current-state document plus the work log and, when applicable, decisions or the asset catalog.
6. Capture concrete user ideas with the lifecycle in `project-prompt.md`; never confuse a proposal with implemented state.
7. Never record secrets, credentials, datastore contents, or unverified guesses in this knowledge base.
