from __future__ import annotations

from client.models import ChatMessage


# Temporary UI mock chat. TODO(C++): Replace with lobby/chat service messages.
MOCK_CHAT: list[ChatMessage] = [
    ChatMessage("global", "MayaStorm", "Queueing arena customs after class.", "09:30", session_id="global"),
    ChatMessage("global", "RenRunner", "Turbo Sprint ghost tables need sorting benchmarks.", "09:41", session_id="global"),
    ChatMessage("scorpions-arena", "Joy", "C++ session handoff placeholder is ready in the launcher.", "09:34", session_id="S-89421"),
    ChatMessage("scorpions-arena", "RenRunner", "Arena queue looks good. Need server broadcast next.", "09:36", session_id="S-89421"),
    ChatMessage("sky-raiders", "Joy", "Sky Raiders is still a polished placeholder entry.", "21:44", session_id="S-89388"),
    ChatMessage("turbo-sprint", "RenRunner", "Ghost time service still needs sorting benchmarks.", "14:12", session_id="S-89310"),
]
