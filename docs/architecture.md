# Architecture

Verified against the live Studio place on 2026-08-31.

## System overview

```text
ReplicatedStorage.Shared
  configs + remotes + animation/VFX assets + client weapon cache
             |                         |
             v                         v
ServerScriptService                StarterPlayer / StarterGui
  LobbyMain                          input, HUD, animation, lobby UI
  CombatInputMain                       |
  Modules                               v
     |                              user intent only
     v                                  |
PlayerData / Party / Run / Gear / Combat / NPC services
     |                                  |
     +-------- authoritative state -----+
             |
             v
DataStoreService, TeleportService, ServerStorage.Enemies,
Workspace.Enemies, player Characters
```

The project is a same-place lobby/run game. Lobby servers manage persistent profiles, class selection, inventory, stats, parties, and queueing. Starting a party reserves a private server for the same place and teleports the party with `TeleportData.ServerMode = "Run"`. The destination server uses the same scripts but initializes in run mode.

## Entry points and ownership

| Entry point | Side | Responsibility |
| --- | --- | --- |
| `ServerScriptService.LobbyMain` | Server | Loads/saves profiles, detects lobby versus run joins, builds client snapshots, handles lobby/party/inventory/stat/consumable remotes, and coordinates run initialization |
| `ServerScriptService.CombatInputMain` | Server | Validates weapon, M1, skill, mana, cooldown, life-state, and sheath requests; dispatches class/skill handlers |
| `StarterPlayer.StarterPlayerScripts.ClientInputHandler` | Client | Routes `UserInputService` begin/end events into config-driven input action modules |
| `StarterPlayer.StarterPlayerScripts.PlayerStatusHudController` | Client | Displays class, level, XP, mana, Humanoid health, and a cloned-character portrait; switches lobby/run UI visibility |
| `StarterPlayer.StarterPlayerScripts.AbilitiesHudController` | Client | Renders four class skill slots and the equipped reusable consumable; animates accepted server cooldowns |
| `StarterPlayer.StarterPlayerScripts.PlayerAnimationController` | Client | Replaces idle/run locomotion and responds to selected class and active weapon state |
| `StarterGui.LobbyUI.*Controller` | Client | Party browser, class selection, inventory/stat allocation, panel coordination, and button presentation |

`StarterPlayer.StarterCharacterScripts.Health` intentionally disables Roblox's default natural health regeneration.

## Server systems

### Persistent player data

`ServerScriptService.Modules.PlayerDataService` owns in-memory sessions and DataStore access.

- DataStore name: `DungeonGameV1`
- Key format: `Player_<UserId>`
- Current schema: `GameDefaults.SchemaVersion = 8`
- Retries: 3 attempts with a fixed 2-second retry delay
- Autosave: every 120 seconds, dispatched per player by `LobbyMain`
- Shutdown: `BindToClose` starts saves and waits for at most 25 seconds
- A failed load creates temporary data with `CanSave = false`, preventing accidental overwrite of stored data.
- A malformed stored value also becomes non-saveable instead of being replaced with default data.
- Saves are serialized per profile and use the loaded `Meta.Revision` as an optimistic concurrency check. A stale server is rejected rather than overwriting a newer revision.
- Mutations made while a save is in flight leave the session dirty for a follow-up save.
- Failed leave saves are retained in memory, retried with backoff, included in shutdown flushing, and reattached if the same user rejoins that server.
- Normalization includes legacy character-slot migration into one profile per class.
- Unknown class profiles are preserved if a matching config is temporarily unavailable.

Persistent root shape:

```text
SchemaVersion
Currency
SelectedClass
Classes[classId]
  Level, Experience, StatPoints
  Stats { Strength, Dexterity, Intelligence, Constitution }
  SkillSlots { Slot1..Slot4 }
Inventory
  Items[itemId] { ConfigId, Quantity }
  Equipped
    Weapon, Consumable
    Armor { Helmet, Chest, Legs, ExtraSlot1, ExtraSlot2 }
Race
SelectedSubclass
Subclasses
Meta { Revision, CreatedAt, UpdatedAt }
```

### Lobby, parties, and teleport queue

`LobbyMain` is the orchestration layer. `PartyService` stores parties in server memory, with a maximum of four members. Parties are indexed by leader and member, listed to all lobby players in that server, and have create/join/leave/kick/start operations.

Client requests pass through `ServerScriptService.Modules.RequestGate`, which uses per-player token buckets. Party broadcasts are emitted only after successful mutations and are coalesced within a scheduler turn.

`RunQueueService` saves valid party members concurrently, calls `TeleportService:ReserveServer(game.PlaceId)`, and teleports the group back into the same place with run-mode teleport data. The teleport payload contains run identity, leader, start time, and a user-ID keyed class selection map. `TeleportInitFailed` clears run-start debounces, cancels the affected party's starting state when it still exists, and republishes party data.

### Run state and resources

`ServerScriptService.Modules.RunService` is a project module; code aliases Roblox's engine service as `RobloxRunService` where both are needed.

- Owns one `ActiveRun` per server and a `PlayerRunData[player]` map.
- Supports lobby combat with a synthetic `RunId = "Lobby"` and reserved-server combat with the real run ID.
- Builds a runtime snapshot containing selected class, class progression, skill slots, raw allocated stats, copied gear, health, mana, keys, and combat loadout.
- Known run states are `WaitingForPlayers` and `Running`.
- `ResourceService` owns mana construction, mutation, and a per-player regeneration task. Base mana is 100, regeneration is 3 every 1 second.
- Player/run change notifications are coalesced before snapshots are sent, and change callbacks no longer build unused deep copies.

### Gear and loadouts

`GearService` owns runtime gear state, class weapon restrictions, loose/equipped item swaps, sheath state, and change callbacks. `GearAppearanceService` clones weapon models from item config ModuleScripts into `Character.Weapons`, prepares their physics, and welds them to R6/R15 hands or torso.

Gear refreshes preserve the current sheath state while rebuilding the runtime appearance.

`CombatLoadoutService` derives:

- An `M1` field from `weaponConfig.M1Skill`; current item configs do not define that field, and authoritative dispatch instead uses the separate `<ClassId>M1` handler convention in `CombatInputMain`.
- Four class skill slots from the saved profile, falling back to `Class.StartingSkills`.
- Global skill slots from `GameDefaults.DefaultGlobalSkillSlots`, currently `Mobility = "Dash"`, with class/runtime override support.

### Combat, skills, and hitboxes

`CombatInputMain` is the authoritative network gate. It rejects invalid slot references, dead players, missing/invalid weapons, class mismatches, insufficient mana, active transitions, concurrent skills, and server cooldown violations.

`ServerScriptService.Modules.CombatPositionService` samples living player roots every 0.1 seconds and maintains the latest accepted combat transform. Horizontal, upward, and downward travel use separate server-side movement budgets. Non-finite or implausible movement blocks combat; large or repeated violations temporarily move the character back to the last accepted root transform under server network ownership. Character replacement invalidates outstanding attack tokens.

Every M1 and skill receives an opaque attack token captured from an accepted transform. `SkillRuntime` resolves that token again at the animation `Hit` marker, so movement during windup must remain plausible and within a bounded horizontal startup envelope. Melee hitboxes use the resolved transform, enforce per-attack range and line of sight, and damage only Humanoids beneath `Workspace.Enemies`. Mage projectiles launch from an authored offset relative to the resolved transform rather than a character weapon part. Invalid spatial validation returns failure before mana or cooldown is committed.

Dash remains camera/movement-direction responsive, but the client direction is only intent. The server fixes speed and duration and registers one bounded, direction-constrained movement allowance with `CombatPositionService`; combat remains blocked for that short movement window.

Runtime dispatch is convention-based:

- M1: `CombatInputMain.Classes.<ClassId>.<ClassId>M1`
- Class skill: `CombatInputMain.Classes.<SkillConfig.Class>.Skills.<SkillId>`
- Shared skill: `CombatInputMain.Classes.Shared.Skills.<SkillId>`

`SkillRuntime` calculates config-driven damage, creates server-replicated VFX/sound, and synchronizes effects to an animation event named `Hit`. `HitboxService` provides one-shot boxes, radii, and server-stepped projectiles. Player attacks exclude all player characters, so the current combat implementation is PvE-only.

Implemented combat handlers are Warrior sword M1, Mage projectile M1, Rogue dagger M1, `PowerStrike`, `WindSlice`, and shared `Dash`.

### NPCs

`NPCHandler` clones templates from `ServerStorage.Enemies`, loads matching configs from `ReplicatedStorage.Shared.Configs.Enemies`, gives NPC parts server network ownership, assigns the `Enemies` collision group, starts movement and attack controllers, and parents live NPCs to `Workspace.Enemies`.

Enemy configs and controller modules are cached after bootstrap. Movement and attack controllers share a short-lived nearest-target cache so they do not independently rescan every player on the same NPC tick.

Enemy config fields select modules by exact name:

- `MovementType = "BasicMovement"`
- `AttackPattern = "Melee"` or `"Ranged"`

Templates currently include `Goblin` and `GoblinRanger`. Each requires a Humanoid, root part, and optional `Idle`, `Walk`, and `Attack` Animation instances.

## Client systems

### Input

Input definitions are child ModuleScripts of `ReplicatedStorage.Shared.Configs.InputActions`. `ClientInputHandler` loads them lazily, ignores processed input and focused text boxes, and calls each matching action's `Began`/`Ended` callback inside `pcall`.

Current bindings:

| Input | Action |
| --- | --- |
| Mouse 1 | Combat M1 |
| Z / X / C / V | Skill slots 1 / 2 / 3 / 4 |
| Q | Global mobility skill (`Dash`) |
| 1 | Equipped reusable consumable |
| R | Toggle weapon sheath |
| Backquote / gamepad Y | Toggle custom inventory |

The client sends intent and immediate press feedback only. The server owns damage, mana, cooldown acceptance, inventory changes, stats, party state, and teleport decisions.

### UI and animation

- `LobbyPanelCoordinator` serializes the three lobby panels through the local `LobbyUI.PanelRequest` BindableEvent.
- `LobbyJoinController` renders in-server party discovery and party membership.
- `ClassSelectionController` discovers class configs dynamically and invokes the server to select one.
- `InventoryController` renders item configs and rarity colors, manages equip/stat requests, disables the CoreGui backpack, locks movement, and uses a scriptable camera while open.
- `ResponsiveUIController` applies runtime `UIScale` instances and layout changes for desktop, compact, and portrait viewports.
- `PlayerStatusHudController` uses server snapshots for progression/mana and the live local Humanoid for health when a character exists.
- `EquippedWeaponCache` is the shared client cache for `GetEquippedWeapon` plus `EquippedWeaponUpdated`.
- `PlayerAnimationController` owns the custom class idle/global run tracks and suppresses conflicting default locomotion while preserving action-priority tracks.

## Primary dependency graph

```text
LobbyMain
  -> PlayerDataService -> GameDefaults, Classes, Races, Items, ExperienceProgression
  -> RequestGate
  -> PartyService
  -> RunQueueService -> PlayerDataService, PartyService, TeleportService
  -> RunService -> GearService, CombatLoadoutService, ResourceService

CombatInputMain
  -> RunService, GearService, Items, Skills, CombatPositionService
  -> class M1/skill handlers -> SkillRuntime, HitboxService, CombatPositionService

GearService
  -> Items, Classes
  -> GearAppearanceService -> item child Models + animation assets

NPCHandler
  -> enemy config modules + ServerStorage enemy templates
  -> BasicMovement + Melee/Ranged attack modules
```

Shared config modules are replicated and consumed on both server and client. Server-only services and handler modules remain under `ServerScriptService`; NPC source templates remain under `ServerStorage`.
