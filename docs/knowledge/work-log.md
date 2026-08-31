# Work log

## 2026-08-31 — Server-validated combat positions

- Added `ServerScriptService.Modules.CombatPositionService` with 0.1-second root sampling, finite-transform checks, separate movement budgets, temporary combat blocking, rate-limited diagnostics, severe/repeated movement correction, character generations, attack tokens, marker-time resolution, and directional movement allowances.
- Routed all M1 and skill dispatch through accepted attack tokens; invalid spatial resolution now fails without committing skill mana or cooldown.
- Replaced live-root and weapon-handle damage origins in Warrior, Rogue, Mage, Power Strike, and Wind Slice with validated attack transforms.
- Added centralized enemy-container, per-attack range, and line-of-sight validation to player hitboxes; server-stepped projectiles now damage only authorized enemies.
- Registered Dash's server-fixed speed/duration as its only bounded directional movement allowance and blocked combat during the brief Dash window.
- Verified the ten changed/new Studio scripts and all 25 `ServerScriptService` Lua sources with static compilation in Edit mode. Audited player attack call sites for live-root/handle origins and authoritative target constraints. An isolated Edit-mode hitbox check confirmed an authorized enemy hit while a wall-blocked target and an out-of-container Humanoid were rejected. No playtest was run because the explicitly excluded enabled dynamic loader would execute with the place.

## 2026-08-31 — Backend persistence and workload hardening

- Added `ServerScriptService.Modules.RequestGate` and applied per-player token buckets to all lobby, party, inventory, class, consumable, combat, sheath, and read remote entry points.
- Serialized profile saves, added optimistic revision rejection, preserved dirty changes made during in-flight writes, rejected malformed stored values, preserved unknown class profiles, and made inventory/profile callback mutations transactional.
- Retained failed leave saves for capped-backoff retry, shutdown flushing, or same-server reattachment instead of discarding the session.
- Coalesced player and party updates, removed unused snapshot deep copies, avoided duplicate class runtime initialization, cached combat handlers and NPC config/controllers, and shared short-lived NPC target scans.
- Saved party members concurrently before teleport, added `TeleportInitFailed` party recovery, preserved sheath state during gear refreshes, and replaced authored server dependency waits with fail-fast references outside the explicitly excluded test spawner.
- Verified all ten changed Studio scripts with static Luau compilation in Edit mode. No playtest was run because the user explicitly excluded the enabled imported dynamic loader from this change; executing the place would still run that known script.

## 2026-08-28 — Persistent idea and documentation workflow

- Added `docs/project-prompt.md` as the reusable Codex project prompt.
- Updated `AGENTS.md` and the `dungeon-game-project` skill so future tasks capture retained ideas with stable IDs and explicit statuses.
- Converted the backlog into an idea registry, retained the Rojo and asset-mapping proposals, and recorded the architecture knowledge base as implemented.
- Added the documentation-impact check and recorded the workflow as decision D-003.

## 2026-08-28 — Read-only Studio architecture audit

- Inspected Dungeon Game (`placeId: 118646628582446`) through Roblox Studio MCP in Edit mode without changing the game or starting a playtest.
- Cataloged server/client entry points, services, configs, data ownership, 14 RemoteEvents, 6 RemoteFunctions, local bindables, important instance paths, runtime-created instances, asset contracts, and naming conventions.
- Added the persistent technical knowledge base at `docs/README.md`, `docs/architecture.md`, `docs/networking.md`, `docs/instance-paths.md`, `docs/conventions.md`, and `docs/known-problems.md`.
- Recorded critical release risks: an obfuscated dynamic server `require` in the imported `Maybedoor` model and unrestricted player-accessible development buttons.
- Recorded confirmed gameplay/design gaps including unused configured stat/derived/defense modifiers, missing DataStore session locking, incomplete run lifecycle, and missing teleport failure recovery.

## 2026-08-28 — Project memory foundation

- Added repository-wide Codex instructions in `AGENTS.md`.
- Added the `dungeon-game-project` repository skill and skill index.
- Added a structured project knowledge base with current state, asset catalog, decisions, backlog, and GitHub status.
- Added repository overview and ignore rules.
- Verified the live Studio connection to Dungeon Game (`placeId: 118646628582446`) in Edit mode.
- Verified local Git identity is configured; GitHub CLI is not installed, the repository has no commits, and no remote is configured.
- Verified the Codex GitHub integration identifies `parkermckinneyCS`, but it currently has no repository installations; the in-app browser GitHub session is signed out.
- Created the repository's initial local commit containing the project assets, skill library, knowledge base, and GitHub workflow files.
- Connected `origin` to `parkermckinneyCS/Roblox-Dungeon-game`, preserved and merged the existing GitHub commit, standardized the local branch as `main`, and prepared the complete project for an approval-gated push.
