# Scene Setup

Create a scene named `BattleRoyaleIsland.unity` and wire these objects:

## Hierarchy

```
GameSystems
├── GameManager
├── ZoneManager (assign SafeZoneCircle child)
├── ItemSpawner
└── BotSpawnManager

Environment
├── Terrain (island)
├── Buildings / Trees / Containers
└── SafeZoneCircle (scaled cylinder, semi-transparent material)

Player
├── CharacterController + PlayerController
├── PlayerHealth + PlayerInventory + SafeZoneDamage
├── WeaponController (child at hand)
├── ParachuteController
└── Tag: Player

UI
├── Canvas (Screen Space Overlay)
│   ├── HUDController
│   ├── MobileInput + joysticks/buttons
│   └── MinimapController
└── EventSystem

Plane
└── PlaneController + plane model
```

## Required Tags

- `Player`
- `Loot` (or add `LootTag` component to loot prefabs)

## NavMesh

1. Mark walkable terrain and building floors as **Navigation Static**.
2. Open **Window > AI > Navigation** and **Bake** the NavMesh.

## Bot Prefab

Attach to a capsule model:

- `NavMeshAgent`
- `EnemyAI`, `BotHealth`, `BotInventory`, `BotVision`
- `ParachuteController`, `SafeZoneDamage`, `AICulling`
- `WeaponController` (child)
- `LootTag` not needed on bot
