"""
generate_npc_sprites.py - Create placeholder NPC sprites

Run this once to generate simple colored idle.png files so the game
runs immediately.  Replace each file with your own 64x64 pixel art
before submitting (Part 3).

Usage:
    python code/game/generate_npc_sprites.py
"""

import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
NPC_DIR = os.path.join(REPO_ROOT, "graphics", "npcs")
SIZE = 64

# (folder_name, fill_color_RGB, label)
PLACEHOLDERS = [
    ("town_elder", (180, 140, 80), "Elder"),
    ("merchant", (80, 160, 80), "Merch"),
    ("sage", (140, 80, 200), "Sage"),
]


def make_placeholder(folder, color, label):
    """Create a placeholder sprite only when idle.png is missing."""
    path = os.path.join(NPC_DIR, folder)
    os.makedirs(path, exist_ok=True)
    img_path = os.path.join(path, "idle.png")

    if os.path.isfile(img_path):
        print(f"  Skipping {img_path} (already exists)")
        return

    try:
        from PIL import Image, ImageDraw, ImageFont

        image = Image.new("RGBA", (SIZE, SIZE), (*color, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(255, 255, 255), width=3)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            font = ImageFont.load_default()
        draw.text((8, 24), label, fill=(255, 255, 255), font=font)
        image.save(img_path)
        print(f"  Created placeholder {img_path}")
    except ImportError:
        _write_minimal_png(img_path, color)
        print(f"  Created placeholder {img_path} (pygame fallback)")


def inspect_sprite(folder):
    """Report whether an NPC sprite exists and whether it is 64x64."""
    img_path = os.path.join(NPC_DIR, folder, "idle.png")
    if not os.path.isfile(img_path):
        print(f"  Missing {img_path}")
        return False

    width = None
    height = None

    try:
        from PIL import Image

        with Image.open(img_path) as image:
            width, height = image.size
    except ImportError:
        pass
    except Exception as exc:
        print(f"  Found {img_path} but could not inspect it with Pillow: {exc}")
        return True

    if width is None:
        try:
            import pygame

            pygame.init()
            image = pygame.image.load(img_path)
            width, height = image.get_size()
            pygame.quit()
        except Exception as exc:
            print(f"  Found {img_path} but could not inspect it with pygame: {exc}")
            return True

    if (width, height) == (SIZE, SIZE):
        print(f"  OK: {img_path} is {SIZE}x{SIZE}")
    else:
        print(f"  WARNING: {img_path} is {width}x{height}, expected {SIZE}x{SIZE}")
    return True


def _write_minimal_png(path, color):
    """Write a simple 64x64 PNG using pygame as a fallback."""
    try:
        import pygame

        pygame.init()
        surface = pygame.Surface((SIZE, SIZE))
        surface.fill(color)
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 3)
        font = pygame.font.SysFont(None, 18)
        label_surface = font.render("NPC", True, (255, 255, 255))
        surface.blit(label_surface, (8, 24))
        pygame.image.save(surface, path)
        pygame.quit()
    except Exception as exc:
        print(f"    Could not create {path}: {exc}")
        print("    Install Pillow or pygame to generate placeholders.")


if __name__ == "__main__":
    print("Checking NPC sprites...")
    for folder, color, label in PLACEHOLDERS:
        exists = inspect_sprite(folder)
        if not exists:
            make_placeholder(folder, color, label)
    print("\nDone. Existing art was preserved; placeholders were created only for missing files.")