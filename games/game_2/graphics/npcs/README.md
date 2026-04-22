# NPC Sprites

Each NPC needs its own subfolder here containing at least one image named `idle.png`.

```
graphics/npcs/
├── town_elder/
│   └── idle.png      ← 64×64 PNG
├── merchant/
│   └── idle.png
└── sage/
    └── idle.png
```

## Requirements (Part 3)

- At least **3 unique NPC sprites** (one per NPC in your dialog_data.py).
- Each sprite must be **64×64 pixels** in PNG format.
- The image must be original art you created (pixel art, digital drawing, etc.).
  Free tools: [Aseprite](https://www.aseprite.org/), [Piskel](https://www.piskelapp.com/),
  [LibreSprite](https://libresprite.github.io/).
- If the folder or `idle.png` is missing, the game will show a blue placeholder
  rectangle — that placeholder earns 0 pts for Part 3.

## Quick start with a placeholder

Run this script from the repo root to generate simple colored placeholder images
while you work on your art:

    python code/game/generate_npc_sprites.py

This creates solid-colour `idle.png` files so the game runs immediately.
Replace each one with real art before submitting.
