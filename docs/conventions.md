# Project conventions and contracts

These are implementation contracts verified in Studio on 2026-08-31. Some are legacy constraints rather than preferred naming.

## Authority and state

- Clients send intent; the server owns persistence, inventory, stats, party membership, teleports, combat acceptance, mana, cooldowns, hit detection, and damage.
- Persistent data belongs to `PlayerDataService`. Runtime combat copies belong to the project `RunService`. Do not mutate snapshots on the client and expect them to persist.
- Lobby and run use the same place and scripts. Determine mode from server-maintained state initialized from `Player:GetJoinData().TeleportData`, not from UI visibility.
- Server state maps are keyed by `Player` objects and must be cleared on `Players.PlayerRemoving`.
- Return fresh snapshots after successful request/response mutations; send update events for asynchronous changes.
- Route every client-to-server entry point through `Modules.RequestGate` before building snapshots, refreshing parties, or rebuilding runtime objects.
- Coalesce asynchronous player and party update events; do not broadcast unchanged state after a rejected mutation.
- Serialize saves per profile and compare the stored `Meta.Revision` with the revision loaded by the session. A conflict must fail closed rather than overwrite.
- Retain a saveable session when its leave-time write fails so it can be retried or reattached on same-server rejoin.

## Config-driven identifiers

Aggregator ModuleScripts discover child ModuleScripts dynamically. The child name is the ID.

- Race IDs: child names under `Configs.Races`.
- Class IDs: child names under `Configs.Classes` and matching folders under `CombatInputMain.Classes`.
- Skill IDs: descendant names under `Configs.Skills`; handler ModuleScript names must match.
- Item IDs: child names under `Configs.Items`; inventory keys and equipped values store these exact names.
- Enemy IDs: child names under `Configs.Enemies` and matching Models under `ServerStorage.Enemies`.
- Input actions: child names under `Configs.InputActions`, each returning a table with `Inputs` and optional `Began`/`Ended` callbacks.

Renaming a config module is a data migration and code/path change, not a cosmetic rename.

## Combat handler layout

- M1 module: `CombatInputMain.Classes.<ClassId>.<ClassId>M1`, returning `module.fire(player, executionContext)`.
- Skill module: `CombatInputMain.Classes.<SkillConfig.Class>.Skills.<SkillId>`, returning `module.fire(player, balance, context)`.
- `SkillConfig.Class` must equal a class ID or `Shared`.
- Numeric skills are `Slot1` through `Slot4`; global slots use string names such as `Mobility`.
- `CombatInputMain` accepts a skill result unless it is literal `false` or a table with `Success = false`; only accepted results deduct mana and start cooldown.
- Do not rely on `CombatLoadout.M1` yet: it reads optional `itemConfig.M1Skill`, while live M1 dispatch and the equipped-weapon payload derive `<ClassId>M1` independently.
- `CombatInputMain` creates a character-bound attack token before dispatch. M1 handlers receive it as `executionContext.AttackToken`; skill handlers receive it in their existing context.
- Animation-driven attacks pass that token to `SkillRuntime.PlayAtHit` and build damage geometry from `marker.AttackCFrame` / `marker.AttackPosition`, never directly from the live root or a weapon part.
- Player attack queries require `Workspace.Enemies` as their target container. Melee attacks also declare a server-owned maximum range and line-of-sight requirement.
- Client vectors may express aim or movement intent only. Server code owns projectile origin/speed/lifetime and movement-ability magnitude/duration; server-authorized movement must be registered with `CombatPositionService`.

## Animation and VFX layout

- Class locomotion/weapon animations: `Assets.Animations.<ClassId>.{M1, Idle, Sheath, Unsheath}`.
- Skill bundle: `Assets.Animations.<ClassId>.Skills.<SkillId>` with an `Animation` child and optional `VFX` children.
- Shared Dash animations: `Assets.Animations.GameAnimations.Skills.Dash.Animations.{W,A,S,D}`.
- Global locomotion: `Assets.Animations.GameAnimations.{Idle, Run}`.
- `SkillRuntime.PlayAtHit` requires an animation event marker named exactly `Hit` and falls back to a timeout. Mage M1 separately accepts `HIT` or `Hit`. Sheath transitions use a keyframe named `Hit`.
- VFX are currently created on the server and replicate to clients; account for replication cost when adding effects.

## Weapon model contract

Every weapon item config can set `ModelName`; its Model lives as a child of the item ModuleScript.

For all weapons:

- Include a descendant BasePart named `Handle`.
- Include a Weld whose `Part0` is the Handle; it is used as the hand weld.
- A functional sheath transition also requires a Weld named `Sheath` with `Part0` set to Handle.
- Runtime code makes all parts unanchored, noncollidable, non-touchable, non-queryable, and massless.

For `WeaponType = "Daggers"`:

- The source model represents the right dagger and requires a Weld named `RightWeld` plus `Handle`.
- Runtime code clones it for the left side and renames the cloned weld `LeftWeld`.
- Characters may be R15 (`RightHand`/`LeftHand`, `UpperTorso`) or R6 (`Right Arm`/`Left Arm`, `Torso`).

## Data and inventory schema

- Increment `GameDefaults.SchemaVersion` when persistent shape or migration semantics change.
- Keep normalization/migration in `PlayerDataService`; never trust stored types or old fields.
- Stats are nonnegative whole numbers named `Strength`, `Dexterity`, `Intelligence`, and `Constitution`.
- Class profiles independently own level, XP, unspent points, stats, and four skill slots.
- Inventory is shared across classes. Weapons are class-restricted when equipped; armor and consumables currently are not class-restricted.
- Loose item records use `{ ConfigId = itemId, Quantity = integer }`; legacy numeric quantities are still tolerated.
- Equipped armor IDs are nested beneath `Inventory.Equipped.Armor`; weapon and consumable IDs are direct children of `Equipped`.
- Potions currently declare `Reusable = true`; use does not decrement quantity by design.

## UI path contracts

- Controllers use extensive `WaitForChild` lookups. GUI instance names are runtime contracts.
- Preserve the current exact names `Inventory UI` and `ConsumeableFrame` until doing a coordinated migration.
- `LobbyUI.PanelRequest` accepts `(panelName, shouldOpen)` for `JoinFrame`, `ClassFrame`, or `Inventory UI`.
- Generated UI clones are identified by attributes rather than names alone.
- Responsive and feature controllers create some local UI helpers at runtime; do not assume every runtime child should be authored back into StarterGui.

## Naming and service aliases

- Project module `ServerScriptService.Modules.RunService` shadows Roblox's `RunService`; use `RobloxRunService` for the engine service when both appear in one script.
- Prefer unique, identifier-safe instance names for new scripted content. Existing spaces, duplicate map names, and misspellings are legacy path constraints.
- Keep test-only server scripts behind an explicit `RunService:IsStudio()` or private authorization guard; the current Workspace test tools violate this convention and are tracked as a problem.
- Required authored server dependencies use direct references and fail immediately during bootstrap. Reserve `WaitForChild` for genuinely replicated or runtime-created instances; do not use an unbounded wait to hide a broken authored path.
