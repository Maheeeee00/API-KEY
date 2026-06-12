# Offline Battle Royale (Free Fire Style)

An offline Unity battle royale prototype: **1 human player + 49 AI bots** on an island map with parachute drops, loot, shrinking safe zones, and mobile-friendly controls.

## Project Location

Open the Unity project in:

```
OfflineBattleRoyale/
```

**Requirements:** Unity 6 (2023 LTS or newer recommended), AI Navigation package.

## Features

| System | Description |
|--------|-------------|
| **Match flow** | Plane flyover → parachute drop → loot → fight → last one standing |
| **50 players** | 1 player + 49 bots with NavMesh pathfinding |
| **Loot** | AK47, SCAR, MP40, M1014, AWM, medkits, helmets, vests, backpacks |
| **Safe zone** | Shrinking circle with outside damage |
| **Bot AI** | State machine: looting, running to zone, attacking, seeking cover |
| **Performance** | `AICulling` disables bots beyond 150m from the player |
| **Mobile UI** | Virtual joysticks, fire/jump/heal/reload buttons, minimap, HUD |

## Architecture

```
Assets/Scripts/
├── Player/       PlayerController, health, inventory, camera
├── AI/           EnemyAI, bot health/inventory/vision, spawner, culling
├── Game/         GameManager, ZoneManager, safe zone damage
├── Items/        Loot spawner and pickups
├── Weapons/      Weapon stats, database, firing logic
├── Drop/         Plane flight and parachute
└── UI/           HUD, minimap, mobile input
```

## Quick Start

1. **Open in Unity** — `File > Open Project` → select `OfflineBattleRoyale/`.
2. **Create the island scene** — Follow `Assets/Scenes/README.md` for hierarchy and component wiring.
3. **Bake NavMesh** — Required for bot movement.
4. **Create loot prefabs** — Weapon/medkit/gear pickups with `LootTag` + pickup scripts.
5. **Assign references** — Wire `GameManager`, `ItemSpawner`, `BotSpawnManager`, and UI in the Inspector.
6. **Press Play** — Jump from the plane (Space), loot weapons, survive the zone.

## Controls

### Desktop (testing)

| Input | Action |
|-------|--------|
| WASD | Move |
| Mouse | Look |
| Left click | Fire |
| R | Reload |
| H | Use medkit |
| Space | Jump / open parachute / exit plane |
| Shift | Sprint |

### Mobile

Use the on-screen joystick (move), right-side buttons (fire, jump, heal, reload), and look joystick.

## Core Scripts (from blueprint)

The three pillars from the design doc are implemented and extended:

- **`PlayerController`** — Movement, shooting, healing (integrates `PlayerInventory` + `WeaponController`)
- **`EnemyAI`** — Bot state machine with looting, zone running, attacking, and cover
- **`ZoneManager`** — Shrinking safe zone singleton with damage outside the circle

## Optimization

`AICulling` turns off `EnemyAI` and `NavMeshAgent` for bots farther than **150 meters** from the player. Re-enable interval: every 1 second. Tighten `cullDistance` on low-end phones.

## Development Roadmap

The blueprint steps map to this repo as follows:

1. **Scene & map** — Build terrain and structures in Unity; scene guide in `Assets/Scenes/README.md`
2. **NavMesh bake** — Documented above
3. **Item spawner** — `ItemSpawner.cs` spawns 100 weighted random loot items
4. **Bot spawning** — `BotSpawnManager.cs` drops 49 bots from altitude with staggered parachutes
5. **Mobile UI** — `MobileInput.cs`, `HUDController.cs`, `MinimapController.cs`

## License

MIT — use freely for learning and prototyping.
