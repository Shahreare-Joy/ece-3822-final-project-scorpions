from __future__ import annotations

from client.models import ChatMessage


class CircularChatBuffer:
    """Fixed-size chat message buffer for a single session.

    This is a client-side scaffold for the UI prototype. It demonstrates why a
    circular buffer/bounded queue fits chat: new messages append in O(1), memory
    stays capped, and the oldest message is overwritten when capacity is full.

    TODO(PROJECT): If the professor requires this as one of the final custom
    structures, document and test it. If not, replace it with your chosen final
    structure while keeping the SessionChat service API stable.
    """

    def __init__(self, capacity: int = 50) -> None:
        if capacity <= 0:
            raise ValueError("Chat buffer capacity must be positive.")
        self.capacity = capacity
        self._items: list[ChatMessage | None] = [None] * capacity
        self._start = 0
        self._count = 0

    def append(self, message: ChatMessage) -> None:
        write_index = (self._start + self._count) % self.capacity
        if self._count == self.capacity:
            self._items[write_index] = message
            self._start = (self._start + 1) % self.capacity
        else:
            self._items[write_index] = message
            self._count += 1

    def recent(self, limit: int | None = None) -> list[ChatMessage]:
        count = self._count if limit is None else min(limit, self._count)
        first = self._count - count
        messages: list[ChatMessage] = []
        for offset in range(first, self._count):
            index = (self._start + offset) % self.capacity
            message = self._items[index]
            if message is not None:
                messages.append(message)
        return messages

    def __len__(self) -> int:
        return self._count
