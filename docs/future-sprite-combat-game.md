# Future Sprite Combat Game

## Important Boundary

FightScope is not a game. FightScope remains an MMA analytics app.

The sprite combat game is a separate future project, likely deployable on GitHub Pages / github.io.

Do not add game mechanics to FightScope unless explicitly requested later.

## Core Concept

A pixel-art combat game using the current cyberpunk martial-arts sprite system.

The player fights waves or groups of mobs and learns new combat moves over time.

Moves can have different rarities and unlock paths.

## Core Gameplay Loop

1. Player enters a stage or fight area.
2. Mobs appear.
3. Player uses learned moves to fight.
4. Defeating mobs gives rewards.
5. Rewards can include new moves, upgraded moves, currency, or unlock materials.
6. Player builds a custom move set.
7. Harder mobs require better movement, timing, combos, and move synergy.

## Move Rarity System

Possible rarity tiers:

* Common
* Uncommon
* Rare
* Epic
* Legendary
* Mythic

Example move categories:

* Striking
* Muay Thai
* Kung Fu
* Wrestling
* Judo / Throws
* Submissions
* Escapes
* Mobility
* Defensive counters
* Special moves, later

Important:
Energy blasts, projectiles, and more game-like abilities may be added in the future game project, but they should not be added to FightScope right now.

## Possible Move Examples

Striking:

* Jab-cross
* Low kick
* Round kick
* Teep
* Elbow
* Palm strike
* Chain punches
* Spinning kick

Standing grappling:

* Collar tie
* Over-under pummeling
* Arm drag
* Snap down
* Clinch knee
* Clinch break

Wrestling:

* Single leg
* Double leg
* Fireman's carry
* Mat return
* Sprawl go-behind

Throws:

* Hip throw
* Judo toss
* Outside trip
* Sweep throw

Submissions:

* Guillotine
* Rear-naked choke
* Armbar
* Triangle
* Front headlock threat

Escapes:

* Sprawl escape
* Stand-up escape
* Scramble reset
* Recovery stance

Future special/game moves:

* Energy blast
* Dash strike
* Shadow counter
* Lightning palm
* Grapple chain finisher
* Area knockback

These future special moves are for the separate game, not FightScope.

## Current Sprite Asset Pipeline

Document the current FightScope sprite pipeline so it can be reused later.

Current known files:

* tools/extract_sprite_frames.py
* app/frontend/public/sprites/sprite-extract-map.json
* app/frontend/public/sprites/sprite-actions.json
* app/frontend/public/sprites/extraction-report.json
* app/frontend/public/sprites/frames/

Current source sprite files:

* app/frontend/public/sprites/source/cyber-ninja-blue.png
* app/frontend/public/sprites/source/shadow-striker-purple.png
* app/frontend/public/sprites/source/cyber-monk-orange.png
* app/frontend/public/sprites/source/neo-operative-green.png
* app/frontend/public/sprites/source/fighter-sparring-reference.png

Current extracted-frame output pattern:

* app/frontend/public/sprites/frames/{character}/{move}/{frameNumber}.png

Known checkpoint from current work:

* 58 transparent runtime frames exported
* 5 manifest characters
* 22 action definitions
* 16 ordered martial-arts source strings preserved
* AmbientFighters reads /sprites/sprite-actions.json
* Latest known sprite-pipeline commit: d782985 Add transparent sprite frame database
* Latest known sprite-animation commit before that: 650c8d1 Animate source sprites and simplify Odds page

## Reusable Technical Direction

The future game should reuse:

* transparent sprite frames
* sprite action manifest
* move categories
* extraction script
* character/action config ideas

The future game should probably have its own repo or separate app folder rather than being mixed directly into FightScope.

Possible future deployment:

* GitHub Pages
* static React app
* Vite or Next static export
* simple browser-local game loop

## Possible Future Game Systems

* Player health
* Mob health
* Stamina or energy
* Move cooldowns
* Combo chains
* Move rarity
* Move upgrades
* Enemy types
* Boss mobs
* Stage progression
* Unlockable characters
* Move drops
* Inventory/loadout screen
* Training mode
* Sprite animation preview screen

## FightScope Boundary Rules

Do not add these to FightScope right now:

* health bars
* player controls
* mob waves
* stages
* game menu
* character select
* damage numbers
* move inventory
* rarity drops
* energy blasts
* projectiles
* sound effects
* win/loss states

FightScope should only keep the sprites as small visual polish.

## Open Questions

* Should the future game be a separate repo or a folder inside the existing repo?
* Should the game use the same four fighters or create a new cast?
* Should moves be learned randomly, through training, or through mob drops?
* Should combat be keyboard-controlled, click/tap based, or auto-battler style?
* Should the rarity system affect power, animation, cooldown, or combo utility?
* Should the game be side-scrolling, arena-based, or roguelite wave-based?

## Next Step Later

When ready, create a separate project plan for:
"Cyberpunk Sprite Combat Game MVP"

Possible MVP:

* one player character
* one mob type
* three moves
* one stage
* basic health
* keyboard movement
* attack button
* one unlockable rare move
* deploy to GitHub Pages

Do not implement this now.
