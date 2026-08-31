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

## D-003 — Preserve user ideas with an explicit lifecycle

- Date: 2026-08-28
- Status: Accepted
- Decision: Record concrete project ideas the user wants retained as stable entries in `backlog.md`, with explicit statuses from proposal through implementation or rejection. Require a documentation-impact check before completing material work.
- Reason: The project should retain evolving product direction without allowing brainstorms or accepted plans to masquerade as verified implementation.
- Consequences: Future Codex tasks follow `docs/project-prompt.md`; accepted durable choices go into the decision log, implemented ideas update current-state documentation and the work log, and secrets or casual examples are never persisted.

## D-004 — Reject stale profile writes and retain failed leave saves

- Date: 2026-08-31
- Status: Accepted
- Decision: Serialize each in-server profile's saves, compare its loaded revision inside `UpdateAsync`, reject stale or malformed stored state, and retain failed leave snapshots for retry or same-server reattachment.
- Reason: A stale session or transient DataStore failure must not overwrite newer data or discard the only current snapshot.
- Consequences: Concurrent sessions fail closed after the first writer advances the revision. A future exclusive session lease may improve the recovery experience, but destructive last-write-wins behavior is prohibited.

## D-005 — Bound remote work before expensive processing

- Date: 2026-08-31
- Status: Accepted
- Decision: Apply per-player token buckets to every client-to-server entry point, coalesce asynchronous snapshots, and broadcast party state only after successful mutations.
- Reason: Validation alone does not prevent exploiters from repeatedly triggering deep copies, model rebuilds, player scans, or lobby-wide network fanout.
- Consequences: Rate-limited mutation calls return a lightweight rejection, read calls may return `nil` when over budget, and new remotes must define an explicit request-gate policy.
