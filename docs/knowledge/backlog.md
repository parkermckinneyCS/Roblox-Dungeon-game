# Backlog and idea registry

This is the durable home for proposed, accepted, in-progress, blocked, rejected, superseded, and implemented ideas. An entry's status is authoritative; discussion alone never means implementation.

## Active ideas

### IDEA-001 — Adopt filesystem-to-Studio source synchronization

- Introduced: 2026-08-28
- Status: Proposed
- Intent: Decide whether to adopt Rojo or another workflow so Git can version and reproduce the live Studio Luau source and hierarchy.
- Affected areas: Repository layout, Studio workflow, GitHub visibility, deployment, and collaboration.
- Open questions: Whether Rojo is the preferred tool, which instances should be source-managed, and how existing live Studio work should be imported safely.
- Links: `docs/README.md`, `docs/knowledge/project.md`

### IDEA-002 — Map local images to Roblox assets and consumers

- Introduced: 2026-08-28
- Status: Proposed
- Intent: Connect each project-owned local image to its Roblox asset ID and the UI or gameplay instances that consume it.
- Affected areas: `UIAssets/`, `assets/`, `docs/knowledge/asset-catalog.md`, and live image properties.
- Open questions: Which local files are canonical, which are references only, and which asset IDs are current.
- Links: `docs/knowledge/asset-catalog.md`

## Completed foundations

### IDEA-003 — Persistent Studio architecture knowledge base

- Introduced: 2026-08-28
- Status: Implemented
- Intent: Preserve the game's systems, dependencies, instance paths, remotes, responsibilities, conventions, and known problems for future agents.
- Affected areas: `docs/` and the repository project workflow.
- Open questions: None for the initial audit; documents must remain synchronized as the live place changes.
- Links: `docs/README.md`, `docs/knowledge/work-log.md`

## Entry template

```markdown
### IDEA-### — Short title

- Introduced: YYYY-MM-DD
- Status: Proposed | Accepted | In progress | Blocked | Implemented | Rejected | Superseded
- Intent: What outcome the user wants and why.
- Affected areas: Systems, UI, assets, data, or paths likely involved.
- Open questions: Only decisions that materially affect the result.
- Links: Relevant decision, implementation, or architecture documents.
```
