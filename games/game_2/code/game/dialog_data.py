"""
dialog_data.py - NPC dialog tree definitions

Author: [Your Name]
Date:   [Date]
Lab:    Lab 7 - NPC Dialog with Graphs

TODO (Part 2)
-------------
Define at least THREE NPCs below, each with a meaningful dialog tree.

Requirements for full credit:
  * At least 3 distinct NPCs (different names, positions, sprites).
  * Each NPC must have at least 4 dialog nodes.
  * At least one NPC must have a BRANCHING tree (a node with 2+ choices
    leading to different destinations).
  * At least one NPC must have a LOOP (an edge that leads back to an
    earlier node, e.g. a merchant menu the player can revisit).
  * At least one NPC must use an AI node connected to Gemini (Part 4).

TODO (Part 4)
-------------
  * Create an AIHandler with a custom personality string.
  * Set at least one dialog node's type to "ai".
  * Add the handler to the matching entry in NPC_DATA.
  * Make sure your GEMINI_API_KEY is set (see ai_npc.py).

NPC_DATA format
---------------
Each entry is a dict with these keys:

    "name"       : str  — displayed in the dialog box header
    "grid_x"     : int  — tile column on the map
    "grid_y"     : int  — tile row on the map
    "sprite_name": str  — subfolder name under graphics/npcs/
    "dialog"     : DialogGraph instance (built by a helper function below)
    "ai_handler" : AIHandler | None  — set to an AIHandler for AI nodes

Adjust grid_x / grid_y so each NPC stands in a walkable area of YOUR map.
"""

from dialog_graph import DialogGraph

# Uncomment when you implement Part 4:
# from ai_npc import AIHandler


# ---------------------------------------------------------------------------
# Example NPC 1 — Town Elder
# ---------------------------------------------------------------------------
# Demonstrates: branching tree, loop back, end node.
# Keep, replace, or extend this as one of your three NPCs.

def _make_town_elder():
    dg = DialogGraph("Town Elder")

    dg.add_dialog_node(
        "greet",
        "Ah, a new face! Welcome to the village. What brings you to my door?"
    )
    dg.add_dialog_node(
        "quest",
        "Dark creatures have been sighted near the old forest to the north. "
        "We need a brave soul to investigate before anyone else goes missing."
    )
    dg.add_dialog_node(
        "lore",
        "This village was founded three centuries ago by a wandering band of "
        "scholars. The great library at the centre holds many forgotten secrets."
    )
    dg.add_dialog_node(
        "accept",
        "Brave and noble! Return to me when you have news. "
        "May the old gods watch over you."
    )
    dg.add_dialog_node(
        "decline",
        "I understand — the path is perilous. Should you change your mind, "
        "the offer stands."
    )
    dg.add_dialog_node("farewell", "Safe travels, adventurer.", node_type="end")

    # Branching from greet
    dg.add_choice("greet",   "quest",    "Tell me about the quest.")
    dg.add_choice("greet",   "lore",     "What can you tell me about this place?")
    dg.add_choice("greet",   "farewell", "Nothing, thanks. Goodbye.")
    # Quest branch
    dg.add_choice("quest",   "accept",   "I'll look into it.")
    dg.add_choice("quest",   "decline",  "That sounds too dangerous for now.")
    # Lore loops back (loop example)
    dg.add_choice("lore",    "greet",    "Interesting. What else can you tell me?")
    dg.add_choice("lore",    "farewell", "Thank you, elder.")
    # End branches
    dg.add_choice("accept",  "farewell", "Farewell.")
    dg.add_choice("decline", "farewell", "Farewell.")

    dg.set_start("greet")
    return dg


# ---------------------------------------------------------------------------
# TODO: Add your own NPCs below.
# Replace these stubs with your implementations.
# ---------------------------------------------------------------------------

# def _make_merchant():
#     dg = DialogGraph("Merchant")
#     # ...
#     dg.set_start("menu")
#     return dg


# def _make_sage():
#     dg = DialogGraph("Elara the Sage")
#     # Add an AI node:
#     #   dg.add_dialog_node("wisdom", "...", node_type="ai")
#     # ...
#     dg.set_start("intro")
#     return dg


# ---------------------------------------------------------------------------
# AI handlers for Part 4
# ---------------------------------------------------------------------------
# Create an AIHandler for each NPC that has an "ai" node.
# Example:
#
#   elder_ai = AIHandler(
#       personality=(
#           "You are a wise village elder in a fantasy RPG. "
#           "Speak formally. Keep replies under 3 sentences."
#       )
#   )

# ---------------------------------------------------------------------------
# NPC_DATA — the game spawns every entry in this list
# ---------------------------------------------------------------------------

NPC_DATA = [
    {
        "name":        "Town Elder",
        "grid_x":      10,
        "grid_y":       5,
        "sprite_name": "town_elder",
        "dialog":      _make_town_elder(),
        "ai_handler":  None,            # TODO (Part 4): replace with AIHandler
    },
    # TODO: Add at least two more NPCs:
    # {
    #     "name":        "Merchant",
    #     "grid_x":      20,
    #     "grid_y":       8,
    #     "sprite_name": "merchant",
    #     "dialog":      _make_merchant(),
    #     "ai_handler":  None,
    # },
    # {
    #     "name":        "Elara the Sage",
    #     "grid_x":      25,
    #     "grid_y":      14,
    #     "sprite_name": "sage",
    #     "dialog":      _make_sage(),
    #     "ai_handler":  sage_ai,       # AIHandler instance from Part 4
    # },
]
