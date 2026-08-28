# Networking contract

Verified against `ReplicatedStorage.Shared.Remotes` on 2026-08-28. The project defines **14 RemoteEvents** and **6 RemoteFunctions**.

## Client-to-server RemoteEvents

| Remote | Client producer | Arguments | Server owner and validation |
| --- | --- | --- | --- |
| `CombatM1` | Input action `CombatM1` | none | `CombatInputMain`; requires living player, initialized combat data, active allowed weapon, no M1 or sheath transition, and a valid `<ClassId>M1` handler |
| `CombatSkill` | `CombatSkill1..4`, `MobilitySkill` | numeric slot 1-4, or global slot name; mobility also sends direction name and world direction | `CombatInputMain`; validates slot, loadout, class, weapon, life state, mana, concurrency, cooldown, and handler |
| `ToggleWeaponSheath` | `ToggleWeaponSheath` input action | none | `CombatInputMain`; requires living player, equipped weapon, valid class, and no conflicting action/transition |
| `UseConsumable` | `UseConsumable` input action | none | `LobbyMain`; validates cooldown, equipped reusable potion, restore type, and whether restoration is needed |
| `CreateParty` | `LobbyJoinController` | none | `LobbyMain` delegates to `PartyService` |
| `JoinParty` | `LobbyJoinController` | leader user ID | `PartyService` validates membership, target party, size, and starting state |
| `LeaveParty` | `LobbyJoinController` | none | `PartyService`; leader departure disbands the party |
| `KickPartyMember` | `LobbyJoinController` | member user ID | `PartyService`; leader-only, cannot kick self |
| `StartParty` | `LobbyJoinController` | none | `PartyService`/`RunQueueService`; leader-only, prevents duplicate starts, validates members/classes before save and teleport |

## Server-to-client RemoteEvents

| Remote | Server producer | Client consumers | Payload |
| --- | --- | --- | --- |
| `PlayerDataUpdated` | `LobbyMain` | status HUD, abilities HUD, player animation, class selection, inventory | Lobby snapshot after persistent/lobby changes |
| `RunDataUpdated` | `LobbyMain` via `RunService` change callback | status HUD, abilities HUD, player animation, inventory | Run snapshot after gear, resources, stats, or progression changes |
| `EquippedWeaponUpdated` | `CombatInputMain` via `GearService` callback | `EquippedWeaponCache` | Active weapon payload or `nil`; sheathed weapons are reported inactive |
| `PartyDataUpdated` | `LobbyMain` | `LobbyJoinController` | `{ Party, ListedParties }` for the receiving lobby player |
| `HudCooldownStarted` | `CombatInputMain`, `LobbyMain` | `AbilitiesHudController` | accepted slot reference and remaining duration; currently sent for numeric skills and consumables |

No project code called `FireAllClients` at audit time. Party and data updates are sent per player.

## RemoteFunctions

| Remote | Client callers | Request | Response / owner |
| --- | --- | --- | --- |
| `GetPlayerData` | status HUD, abilities HUD, player animation, class selection, inventory | none | `LobbyMain`; returns the caller's lobby or run snapshot |
| `GetPartyData` | `LobbyJoinController` | none | `LobbyMain`/`PartyService`; returns `{ Party, ListedParties }` |
| `SelectClass` | `ClassSelectionController` | class ID | `LobbyMain`/`PlayerDataService`; `{ Success, Message, Data }` |
| `GetEquippedWeapon` | `EquippedWeaponCache` | none | `CombatInputMain`; active weapon payload or `nil` |
| `ToggleInventoryEquip` | `InventoryController` | `{ Mode = "Equip", ItemId, PreferredSlotId? }` or `{ Mode = "Unequip", SlotId }` | `LobbyMain`/`PlayerDataService`/`GearService`; validated result plus fresh snapshot |
| `ApplyStatPoints` | `InventoryController` | `{ ClassId, Additions = { statName = nonnegative integer } }` | `LobbyMain`/`PlayerDataService`; lobby-only validated result plus fresh snapshot |

## Snapshot shapes

Lobby snapshot:

```text
{
  ServerMode = "Lobby",
  Currency,
  DataLoaded,
  PlayerData,          -- complete persistent client snapshot
  SelectedCharacter,  -- compatibility view of selected class profile
  RunPlayerData        -- lobby combat state when initialized
}
```

Run snapshot:

```text
{
  ServerMode = "Run",
  Currency,
  ActiveRun,
  RunPlayerData
}
```

The UI deliberately accepts both current fields and some legacy compatibility fields. When changing a snapshot, search all five snapshot consumers before removing or renaming data.

## Local bindables

| Bindable | Location | Purpose |
| --- | --- | --- |
| `ClientAbilityActivated` | `ReplicatedStorage.Shared` | Local input-to-HUD press feedback; it never crosses the network |
| `PanelRequest` | `StarterGui.LobbyUI` | Local coordination so only one lobby panel is open |

## Trust boundary

All remote arguments are untrusted. Existing gameplay mutations are server-side and the main handlers validate type, authority, class/loadout state, life state, inventory, mana, and cooldown as applicable. New remotes should follow the same pattern and must never accept client-supplied damage, rewards, inventory quantities, or final positions as authoritative values.
