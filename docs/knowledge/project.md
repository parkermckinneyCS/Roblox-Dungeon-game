# Project snapshot

Last verified: 2026-08-31

## Identity

- Project: Dungeon Game
- Platform: Roblox
- Connected Studio place: `Dungeon Game`
- Place ID: `118646628582446`
- Last observed Studio mode: Edit

## Repository state

- The repository contains project assets and a persistent architecture knowledge base, but no Rojo project file or checked-in Luau source tree was present at the last verification.
- The live Studio place remains the source of truth for scripts and DataModel structure; GitHub does not yet contain the full game implementation.
- `UIAssets/` contains extracted or prepared UI imagery and Python inspection/extraction helpers.
- `assets/` contains gameplay and consumable visual assets.
- `.agents/skills/` contains repository-scoped Codex workflows.
- `docs/` contains the architecture, networking, path, conventions, and known-problem references.
- `docs/knowledge/` contains identity, decisions, assets, backlog, GitHub state, and work history.

## Verified live architecture

- The same Roblox place handles both Lobby and Run server modes. Parties reserve and teleport to a private server of `game.PlaceId` with run-mode teleport data.
- `ServerScriptService.LobbyMain` orchestrates data, lobby/run initialization, parties, inventory/stats, consumables, snapshots, autosave, and shutdown saves.
- `ServerScriptService.CombatInputMain` is the server-authoritative combat/sheath remote gateway.
- Server modules own player data, parties, run state, teleport queueing, mana, gear/appearance, combat loadouts, skills/hitboxes, and NPCs.
- `ServerScriptService.Modules.RequestGate` bounds every current client-to-server entry point with per-player token buckets.
- Profile writes are serialized, revision-checked, and retain failed leave saves for retry; malformed stored values fail closed.
- Player and party update pushes are coalesced, party members save concurrently before teleport, and server-side teleport initialization failures cancel stale party-start state.
- NPC config/controller lookup is cached and movement/attack controllers share short-lived target scans.
- `ReplicatedStorage.Shared` owns shared config registries, 14 RemoteEvents, 6 RemoteFunctions, client weapon cache, and animation/VFX assets.
- Client controllers under `StarterPlayerScripts` and `StarterGui` own input routing, HUD, locomotion animation, party/class/inventory UI, panel coordination, and responsive layout.
- NPC templates are in `ServerStorage.Enemies`; live NPCs are parented to `Workspace.Enemies`.
- Full details are indexed from `docs/README.md`.

## Working conventions

- Treat filenames containing `reference` as source/visual references, `exact` as close crops or matches, `dynamic` as runtime-oriented variants, and `8x` as enlarged inspection versions unless later work establishes a different meaning.
- Keep source references and derived variants together within their feature category.
- Treat config ModuleScript names as durable IDs; class, skill, item, enemy, and handler names are coupled across exact paths.
- Preserve server authority for persistence, inventory, stats, parties, teleports, combat, resources, hit detection, and damage.
- Preserve exact legacy GUI names such as `Inventory UI` and `ConsumeableFrame` until all paths are migrated together.
- Read `docs/conventions.md` before adding configs, skills, weapons, remotes, or UI controllers.

## Known gaps

- Live Studio source is not mirrored or synced into Git, so the repository cannot reproduce the place from source.
- The local repository is connected to `https://github.com/parkermckinneyCS/Roblox-Dungeon-game` as `origin`.
- The asset upload/usage mapping between local PNGs and Roblox asset IDs has not been documented.
- Security and gameplay issues found during the audit are tracked in `docs/known-problems.md`; the imported door loader and unrestricted test buttons are release blockers.
