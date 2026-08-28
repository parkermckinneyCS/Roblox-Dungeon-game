# Decision log

## D-001 — Version project memory with the repository

- Date: 2026-08-28
- Status: Accepted
- Decision: Store project instructions in `AGENTS.md`, reusable project workflows in `.agents/skills/`, and durable project facts under `docs/knowledge/`.
- Reason: This keeps team and Codex context reviewable, portable, and synchronized through Git rather than tied to one chat.
- Consequences: Material project work must update the smallest relevant knowledge files. One-off details should not become permanent rules.

## D-002 — Separate current state, history, and future work

- Date: 2026-08-28
- Status: Accepted
- Decision: Keep verified current state in `project.md`, append-only choices in `decisions.md`, completed work in `work-log.md`, and unimplemented ideas in `backlog.md`.
- Reason: Mixing these concerns makes stale plans look like implemented facts.
- Consequences: New entries must be placed according to their meaning, and superseded decisions remain visible.
