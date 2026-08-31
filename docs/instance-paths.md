# Important Studio instance paths

Verified in the Edit DataModel on 2026-08-31. Paths omit the optional `game.` prefix.

## Shared replicated contract

```text
ReplicatedStorage.Shared
├── EquippedWeaponCache (ModuleScript)
├── ClientAbilityActivated (BindableEvent)
├── Remotes
├── Configs
│   ├── GameDefaults
│   ├── Races/{Human, Elf}
│   ├── Classes/{Warrior, Mage, Rogue}
│   ├── Skills/{Warrior/PowerStrike, Mage/WindSlice, Shared/Dash}
│   ├── InputActions/{CombatM1, CombatSkill1..4, MobilitySkill,
│   │                 UseConsumable, ToggleWeaponSheath}
│   ├── Items/{15 item config modules}
│   ├── Rarities
│   ├── ExperienceProgression
│   └── Enemies/{Goblin, GoblinRanger}
└── Assets.Animations
    ├── Warrior/{M1, Idle, Sheath, Unsheath, Skills/PowerStrike}
    ├── Mage/{M1, Idle, Sheath, Unsheath, Skills/WindSlice}
    ├── Rogue/{M1, Idle, Sheath, Unsheath, Skills}
    └── GameAnimations/{Idle, Run, Skills/Dash, WeaponPacks}
```

The complete remote inventory and directionality are in [`networking.md`](networking.md).

## Server code

```text
ServerScriptService
├── LobbyMain
├── CombatInputMain
│   └── Classes
│       ├── Warrior/{WarriorM1, Skills/PowerStrike}
│       ├── Mage/{MageM1, Skills/WindSlice}
│       ├── Rogue/{RogueM1, Skills}
│       └── Shared/Skills/Dash
└── Modules
    ├── PlayerDataService
    ├── RequestGate
    ├── CombatPositionService
    ├── PartyService
    ├── RunQueueService
    ├── RunService
    ├── ResourceService
    ├── GearService/GearAppearanceService
    ├── CombatLoadoutService
    ├── SkillRuntime
    ├── HitboxService
    └── NPCHandler
        ├── TestSpawner (Script)
        ├── Movement/BasicMovement
        └── AttackPatterns/{Melee, Ranged}
```

## Client code and GUI

```text
StarterPlayer.StarterPlayerScripts
├── ClientInputHandler
├── PlayerStatusHudController
├── AbilitiesHudController
├── ResponsiveUIController
└── PlayerAnimationController

StarterPlayer.StarterCharacterScripts.Health

StarterGui
├── LobbyUI
│   ├── LobbyJoinController
│   ├── ClassSelectionController
│   ├── InventoryController
│   ├── LobbyPanelCoordinator
│   ├── PanelRequest (BindableEvent)
│   ├── SideButtonFrame
│   │   ├── JoinButton
│   │   ├── ClassButton
│   │   └── SideButtonStyleController
│   ├── JoinFrame/{PartyBrowserFrame, PartyViewFrame}
│   ├── ClassFrame/{SelectFrame, TalentFrame}
│   └── Inventory UI/{EquipmentFrame, ItemsBackground, StatsFrame, ItemDescFrame}
└── RunUI
    ├── PlayerStatusHud/{HealthGroup, ManaGroup, PortraitFrame, LevelBadge}
    ├── AbilitiesHud/{SkillSlotHud, ConsumeableFrame}
    └── ExperienceGroup
```

`Inventory UI` contains a space and `ConsumeableFrame` is misspelled in the live hierarchy. They are hard-coded by `WaitForChild`; treat both spellings as API until all callers and instances are migrated together.

## Server-only templates and editor data

```text
ServerStorage
├── Enemies
│   ├── Goblin
│   └── GoblinRanger
└── RBX_ANIMSAVES
```

Enemy templates contain Humanoids, root/body parts, and `Idle`, `Walk`, and `Attack` animations. `RBX_ANIMSAVES` contains numerous animation-editor `ObjectValue` and `KeyframeSequence` saves; it is not referenced by the audited gameplay scripts.

## Workspace

Important authored paths:

- `Workspace.Enemies`: target parent for live NPC clones.
- `Workspace.TestButtons`: 12 ClickDetector-based development controls for inventory, XP, resources, and enemy spawning.
- `Workspace.SpawnLocation`: current spawn.
- `Workspace.Shitty First map`: large authored map model.
- `Workspace.Maybedoor`: imported door model containing the security-critical `LightConfig` script described in [`known-problems.md`](known-problems.md).

The Workspace contains many top-level instances with duplicate names such as `DefaultWall` and `DefaultRock`. A dot path to one of those names is ambiguous. Do not use a bare `Workspace:FindFirstChild("DefaultWall")` as a stable content identifier; introduce unique folders/IDs before scripting against map pieces.

## Runtime-created paths

- `Workspace.Enemies.<enemy clone>`: created by `NPCHandler.Spawn` and destroyed three seconds after Humanoid death.
- `<Player.Character>.Weapons`: rebuilt by `GearAppearanceService`; contains active weapon model clone(s).
- `PlayerGui.LobbyUI`: copy of `StarterGui.LobbyUI` used by client controllers.
- `PlayerGui.RunUI`: copy of `StarterGui.RunUI`; kept enabled in both modes for the shared status HUD.
- `PlayerGui.RunUI.PlayerStatusHud.PortraitFrame.PortraitViewport.CharacterWorld.PortraitCharacter`: local sanitized character clone.
- `LobbyUI` party/inventory generated rows: clones marked with `GeneratedPartyRow`, `GeneratedMemberRow`, or `GeneratedInventoryItem` attributes.
- Ability cooldown overlays and several `UIScale`/text constraint instances are created locally if missing.

## Asset co-location contract

Weapon display models are children of their item config ModuleScript, for example:

```text
ReplicatedStorage.Shared.Configs.Items.TrainingSword.TrainingSword
ReplicatedStorage.Shared.Configs.Items.ApprenticeWand.ApprenticeWand
ReplicatedStorage.Shared.Configs.Items.StarterDaggers.StarterDagger
```

`GearAppearanceService` first looks for `itemConfig.ModelName`, then the first child Model. See [`conventions.md`](conventions.md) before adding weapon models.
