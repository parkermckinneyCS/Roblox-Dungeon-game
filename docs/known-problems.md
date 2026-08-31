# Known technical problems

Verified by static Studio inspection on 2026-08-31. “Confirmed” means the relevant source/path was observed; runtime impact was not playtested unless explicitly stated.

## Critical

### DG-001 — Obfuscated dynamic server `require` in imported door model

Status: **Confirmed security risk; not executed or removed**

Path:

`Workspace.Maybedoor.Meshes/PolygonDungeon_Environments_03_SM_Env_Door_Large_Wood_01.LightConfig`

The server Script contains obfuscated helper code that obtains Marketplace product information, converts the description to a number, stores it in `EasyConfiguration.Pose.Value`, and then calls `require` on that value. The currently inspected `NumberPose.Value` is `90983637061475`. This permits external asset code to execute on the server and change independently of the place. The bundled `Type`/`EasyConfiguration` modules also contain obsolete and suspicious code unrelated to a simple door light.

Treat this as untrusted/backdoor-like code. Before any public release, quarantine or remove the script and inspect the door for other imported scripts. Do not execute the dynamic require merely to identify it.

### DG-002 — Player-accessible development controls can mutate live data

Status: **Confirmed**

`Workspace.TestButtons` contains 12 ClickDetector controls, and `ServerScriptService.Modules.NPCHandler.TestSpawner` wires enemy spawn buttons. The scripts have no `RunService:IsStudio()` or authorization guard. Any player who can reach/click them can clear or grant inventory, change XP/level, heal/damage/reset mana, or spawn enemies. Some of these operations mark persistent profile data dirty and may autosave.

Before release, move these tools out of production or add a server-side Studio/private tester gate.

## High

### DG-003 — Configured class, race, item, and armor modifiers are not applied

Status: **Confirmed gameplay defect/design gap**

`StatModifiers`, `DerivedStatModifiers`, and armor `Defense` are present in configs but have no gameplay consumer. `RunService` copies only the class profile's raw allocated `Stats`; max health reads `stats.MaxHealth` and otherwise becomes 100, while `ResourceService.BuildMana()` always starts from base mana 100. Incoming NPC damage calls `Humanoid:TakeDamage` directly without armor mitigation.

Consequences include Warrior `MaxHealth +25`, Mage/Elf/wand max-mana bonuses, class/race base stats, weapon/armor stat bonuses, and armor defense having no effect. The inventory tooltip can display item stat modifiers even though combat does not apply them.

### DG-004 — DataStore uses optimistic conflict rejection without an exclusive session lock

Status: **Mitigated on 2026-08-31; destructive stale writes are rejected**

`PlayerDataService.Save` now serializes writes for each in-server session and compares the stored `Meta.Revision` with the revision loaded by that session inside `UpdateAsync`. Stale sessions and malformed stored values are rejected instead of overwriting newer or recoverable data. Mutations made during a save remain dirty for a follow-up write, and failed leave saves are retained and retried.

There is still no cross-server lease or exclusive ownership lock. If two live servers load the same revision, the first successful writer wins and the other session becomes non-saveable after its conflict is detected. This preserves stored data but requires a future reconnect/recovery experience if concurrent sessions are common.

### DG-005 — Run lifecycle stops at `Running`

Status: **Confirmed incomplete system**

The only observed run states are `WaitingForPlayers` and `Running`. There is no completion/failure state, reward settlement, dungeon objective controller, return-to-lobby teleport, or explicit active-run teardown. Party teleport starts a reserved server, but the gameplay loop after arrival is not implemented by the audited scripts.

## Medium

### DG-006 — Teleport failure recovery is incomplete

Status: **Resolved on 2026-08-31 for server-side party recovery**

`RunQueueService` now retains the start debounce after `TeleportAsync`, listens for `TeleportInitFailed`, clears affected member debounces, and asks `LobbyMain` to cancel and republish the party's starting state when that party still exists. A dedicated user-facing teleport error message is still not implemented.

### DG-007 — Party discovery is limited to one lobby server

Status: **Confirmed architectural limitation**

`PartyService` is in-memory only and no `MemoryStoreService` or cross-server messaging was found. Players can only browse/join parties hosted in their current public server. There are no invites, privacy controls, leader transfer, or matchmaking.

### DG-008 — NPC navigation has no pathfinding

Status: **Confirmed**

`NPCHandler.Movement.BasicMovement` repeatedly calls `Humanoid:MoveTo` toward the nearest player. It does not use `PathfindingService`, waypoints, stuck detection, or obstacle recovery, so NPCs are likely to fail in complex dungeon geometry.

### DG-009 — Debug hitboxes are visible in normal gameplay

Status: **Confirmed**

NPC melee always creates a neon `GoblinAttackHitbox`. Warrior and Rogue M1 handlers call the shared hitbox service with visualization enabled. These server-created parts replicate to clients and have no Studio/debug flag.

### DG-010 — Wind Slice VFX hook is empty

Status: **Confirmed**

`CombatInputMain.Classes.Mage.Skills.WindSlice.attachWindSliceVFX` finds the skill VFX folder but does nothing. Authored emitters under `Assets.Animations.Mage.Skills.WindSlice.VFX.WindSliceVFX` are therefore not attached to the projectile by this handler.

### DG-011 — Mobility feedback/cooldown is not represented by the abilities HUD

Status: **Confirmed UI gap**

The Q input fires local activation name `MobilitySkill`, but `AbilitiesHudController.frameByActivation` has entries only for skill slots 1-4 and the consumable. `CombatInputMain` sends `HudCooldownStarted` only for numeric slots, not global slots. Dash is server-cooled down but has no corresponding accepted cooldown display.

### DG-012 — Refreshing gear forcibly unsheathes the weapon

Status: **Resolved on 2026-08-31**

`RunService.RefreshPlayerGear` now requests sheath preservation. `GearService.RegisterPlayerGear` rebuilds the appearance and restores the previous sheath attachment without replaying the transition animation.

### DG-017 — Remote requests could amplify server and network work

Status: **Resolved on 2026-08-31**

Lobby, inventory, class, party, combat, and read requests now use per-player token buckets in `Modules.RequestGate`. Failed party requests no longer broadcast lobby-wide snapshots, and successful data/party notifications are coalesced within a scheduler turn.

### DG-018 — Failed leave saves were discarded

Status: **Resolved on 2026-08-31**

`SaveAndRemove` now retains a previously saveable session after a failed leave write, retries it with capped backoff, includes pending saves in shutdown flushing, and reattaches the session if the user rejoins the same server before retry completion.

## Low / maintainability

### DG-013 — Inventory UI creates one GUI clone per item unit

Status: **Confirmed scaling concern**

`InventoryController.renderLooseItems` loops from 1 through each record's quantity and clones a slot per unit. Large stack quantities will increase instance count and render work linearly instead of displaying one stack with a quantity label.

### DG-014 — Workspace paths are ambiguous and include legacy names

Status: **Confirmed**

Workspace contains many duplicate top-level `DefaultWall` and `DefaultRock` instances, plus names with spaces and an unprofessional map name. Duplicate full paths make name-based inspection/scripting ambiguous and complicate automation. Rename/reorganize only as an explicit migration because authored references may depend on current instances.

### DG-015 — Large editor animation-save data remains in the place

Status: **Observed; impact not measured**

`ServerStorage.RBX_ANIMSAVES` contains many animation editor saves and keyframe sequences and was not referenced by audited gameplay code. It may increase place size and editing clutter. Confirm which sequences are still source assets before cleanup.

### DG-016 — Combat loadout M1 metadata diverges from runtime dispatch

Status: **Confirmed maintainability defect**

`CombatLoadoutService` sets `CombatLoadout.M1` from optional `weaponConfig.M1Skill`, but current item configs do not define `M1Skill`. `CombatInputMain` instead derives `<ClassId>M1` directly and returns that in the equipped-weapon payload. Combat works through the class convention, but the loadout field is empty and can mislead future consumers until the two contracts are reconciled.

## Audit limitations and follow-up

- This was a static, read-only Edit-mode audit. No multiplayer, teleport, DataStore, combat, NPC, UI-device, or performance playtest was run.
- Studio output contained plugin/editor messages only during inspection; it is not evidence that runtime paths are error-free.
- Prioritize DG-001 and DG-002 before executing or publishing the place. Then establish automated/runtime tests around data, effective stats, teleport failure, combat validation, and run completion.
