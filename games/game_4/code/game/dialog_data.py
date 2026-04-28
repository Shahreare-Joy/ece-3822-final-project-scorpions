"""
dialog_data.py - NPC dialog tree definitions

Author: Kevin Le
Date:   04/24/2026
Lab:    Lab 7 - NPC Dialog with Graphs
"""

from dialog_graph import DialogGraph
from ai_npc import AIHandler


def _make_town_elder():
    """Build the Town Elder's dialog tree."""
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
        "I understand - the path is perilous. Should you change your mind, "
        "the offer stands."
    )
    dg.add_dialog_node("farewell", "Safe travels, adventurer.", node_type="end")

    dg.add_choice("greet", "quest", "Tell me about the quest.")
    dg.add_choice("greet", "lore", "What can you tell me about this place?")
    dg.add_choice("greet", "farewell", "Nothing, thanks. Goodbye.")
    dg.add_choice("quest", "accept", "I'll look into it.")
    dg.add_choice("quest", "decline", "That sounds too dangerous for now.")
    dg.add_choice("lore", "greet", "Interesting. What else can you tell me?")
    dg.add_choice("lore", "farewell", "Thank you, elder.")
    dg.add_choice("accept", "farewell", "Farewell.")
    dg.add_choice("decline", "farewell", "Farewell.")

    dg.set_start("greet")
    return dg


def _make_merchant():
    """Build the merchant's looping shop-style dialog tree."""
    dg = DialogGraph("Mira the Merchant")

    dg.add_dialog_node("menu", "Welcome, traveler. What catches your eye today?")
    dg.add_dialog_node(
        "potions",
        "Healing draughts, bright as sunrise. One sip and your bruises forget they ever existed."
    )
    dg.add_dialog_node(
        "weapons",
        "Steel for goblins, silver for spirits, and one sword I absolutely do not ask about."
    )
    dg.add_dialog_node(
        "rumors",
        "People whisper about blue lights near the ruins after midnight. I prefer customers to ghosts."
    )
    dg.add_dialog_node("bye", "Come back with coin and curiosity.", node_type="end")

    dg.add_choice("menu", "potions", "Show me your potions.")
    dg.add_choice("menu", "weapons", "What weapons do you sell?")
    dg.add_choice("menu", "rumors", "Heard any rumors lately?")
    dg.add_choice("menu", "bye", "Just browsing. Goodbye.")
    dg.add_choice("potions", "menu", "Let me see the rest of your stock.")
    dg.add_choice("weapons", "menu", "What else do you have?")
    dg.add_choice("rumors", "menu", "Anything else for sale?")

    dg.set_start("menu")
    return dg


def _make_sage():
    """Build the sage's dialog tree with an AI-driven node."""
    dg = DialogGraph("Elara the Sage")

    dg.add_dialog_node(
        "intro",
        "The wind carried your footsteps to me before you arrived. What wisdom do you seek?"
    )
    dg.add_dialog_node(
        "ruins",
        "The ruins remember every oath sworn inside them. Few visitors enjoy being remembered in return."
    )
    dg.add_dialog_node(
        "wisdom",
        "Elara closes her eyes and listens to something older than the room...",
        node_type="ai"
    )
    dg.add_dialog_node(
        "warning",
        "Power without patience rots the hand that holds it. Walk lightly."
    )
    dg.add_dialog_node("farewell", "Then go, and let the stars keep your name.", node_type="end")

    dg.add_choice("intro", "ruins", "Tell me about the ruins.")
    dg.add_choice("intro", "wisdom", "Share a prophecy with me.")
    dg.add_choice("intro", "warning", "Do you have any warning for me?")
    dg.add_choice("intro", "farewell", "I should be going.")
    dg.add_choice("ruins", "intro", "What else should I know?")
    dg.add_choice("wisdom", "intro", "I would hear more.")
    dg.add_choice("warning", "farewell", "I'll remember that.")

    dg.set_start("intro")
    return dg


sage_ai = AIHandler(
    personality=(
        "You are Elara, an ancient sage in a fantasy RPG. "
        "Speak with calm, old-world wisdom and a hint of mystery. "
        "Keep responses under three sentences."
    )
)


NPC_DATA = [
    {
        "name": "Town Elder",
        "grid_x": 10,
        "grid_y": 5,
        "sprite_name": "town_elder",
        "dialog": _make_town_elder(),
        "ai_handler": None,
    },
    {
        "name": "Mira the Merchant",
        "grid_x": 20,
        "grid_y": 8,
        "sprite_name": "merchant",
        "dialog": _make_merchant(),
        "ai_handler": None,
    },
    {
        "name": "Elara the Sage",
        "grid_x": 25,
        "grid_y": 14,
        "sprite_name": "sage",
        "dialog": _make_sage(),
        "ai_handler": sage_ai,
    },
]