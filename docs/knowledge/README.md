# Project knowledge base

This directory is the durable, Git-versioned memory for Dungeon Game. Read this index first, then open only the files relevant to the current task.

| File | Use it for |
| --- | --- |
| [`../README.md`](../README.md) | Technical knowledge index and future-agent start checklist |
| [`../architecture.md`](../architecture.md) | Major systems, dependencies, state ownership, and lifecycle |
| [`../networking.md`](../networking.md) | RemoteEvents, RemoteFunctions, bindables, callers, and handlers |
| [`../instance-paths.md`](../instance-paths.md) | Important live Studio and runtime-created paths |
| [`../conventions.md`](../conventions.md) | Identifier, data, animation, weapon, UI, and authority contracts |
| [`../known-problems.md`](../known-problems.md) | Verified security risks, defects, limitations, and audit gaps |
| [`project.md`](project.md) | Current project identity, verified structure, systems, and conventions |
| [`asset-catalog.md`](asset-catalog.md) | UI and gameplay asset inventory |
| [`decisions.md`](decisions.md) | Durable technical and product decisions |
| [`work-log.md`](work-log.md) | Concise record of completed material work and verification |
| [`backlog.md`](backlog.md) | Open questions and future work; nothing here is assumed implemented |
| [`github.md`](github.md) | Repository and GitHub connection state |

## Maintenance rules

- Prefer short, verified statements with paths or Studio instance names.
- Treat the architecture documents one directory above as current-state references and update the affected document after Studio architecture changes.
- Update current-state documents rather than appending duplicate facts.
- Append decisions and work-log entries chronologically; supersede decisions explicitly.
- Separate confirmed facts from assumptions and future plans.
- Never store secrets or authentication material here.
