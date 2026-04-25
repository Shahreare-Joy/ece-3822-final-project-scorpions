from __future__ import annotations

"""Custom max-heap / priority queue.

Use cases:
- top-N leaderboard scores
- popular games by active players
- priority matchmaking queues

Expected complexity:
- push: O(log n)
- pop: O(log n)
- peek: O(1)

TODO (DONE)(HEAP): Implement with custom array-style storage, not Python heapq
as the final assignment solution. Internally this uses a compact Python list for
the backing dynamic array; all heap behavior is implemented manually.
"""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(order=True)
class _HeapItem:
    # store priority for heap ordering
    priority: int

    # store actual value without using it for comparison
    value: object = field(compare=False)


class MaxHeap:
    def __init__(self) -> None:
        # TODO (DONE): store heap nodes in custom Array/dynamic array.

        # backing storage for heap items
        self._items: list[_HeapItem] = []

    def __len__(self) -> int:
        '''return number of items in heap'''
        return len(self._items)

    def push(self, priority: int, value: object) -> None:
        '''insert item and restore max-heap order'''

        # add new item at end
        self._items.append(_HeapItem(priority, value))

        # move item upward until heap order is correct
        self._bubble_up(len(self._items) - 1)

    def heapify(self, records: list[tuple[int, object]]) -> None:
        '''build heap from priority/value pairs'''
        """Build the heap from priority/value pairs."""

        # convert records into heap items
        self._items = [_HeapItem(priority, value) for priority, value in records]

        # restore heap order from last parent down to root
        for index in range((len(self._items) // 2) - 1, -1, -1):
            self._bubble_down(index)

    def pop_max(self) -> object:
        '''remove and return highest-priority value'''

        # reject empty heap
        if not self._items:
            raise IndexError("pop from empty heap")

        # root stores max-priority item
        max_value = self._items[0].value

        # move last item to root position
        last = self._items.pop()

        if self._items:
            self._items[0] = last

            # restore heap order downward
            self._bubble_down(0)

        return max_value

    def pop(self) -> object:
        '''alias for pop_max'''
        return self.pop_max()

    def peek_max(self) -> object:
        '''return highest-priority value without removing it'''

        # reject empty heap
        if not self._items:
            raise IndexError("peek from empty heap")

        return self._items[0].value

    def peek(self) -> object:
        '''alias for peek_max'''
        return self.peek_max()

    def update_priority(self, value: object, new_priority: int) -> bool:
        '''update first matching value priority and restore heap order'''
        """Update the first matching value and restore heap order."""

        # search for first matching value
        for index, item in enumerate(self._items):
            if item.value == value:
                old_priority = item.priority
                item.priority = new_priority

                # move up if priority increased, otherwise move down
                if new_priority > old_priority:
                    self._bubble_up(index)
                else:
                    self._bubble_down(index)

                return True

        return False

    def top_n(self, n: int) -> list[object]:
        '''return top n values without changing original heap'''

        # copy heap into clone
        clone = MaxHeap()
        for item in self._items:
            clone.push(item.priority, item.value)

        results: list[object] = []

        # repeatedly pop max from clone
        while len(clone) and len(results) < n:
            results.append(clone.pop_max())

        return results

    def items(self) -> Iterator[object]:
        '''iterate through heap values in internal heap order'''

        # yield values only, not priorities
        for item in self._items:
            yield item.value

    def _bubble_up(self, index: int) -> None:
        '''move item upward until parent has higher priority'''

        while index > 0:
            # find parent index
            parent = (index - 1) // 2

            # stop if parent is already larger or equal
            if self._items[parent].priority >= self._items[index].priority:
                break

            # swap item with parent
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def _bubble_down(self, index: int) -> None:
        '''move item downward until children have lower priority'''

        size = len(self._items)

        while True:
            # calculate child indexes
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            # compare left child
            if left < size and self._items[left].priority > self._items[largest].priority:
                largest = left

            # compare right child
            if right < size and self._items[right].priority > self._items[largest].priority:
                largest = right

            # stop when heap property is correct
            if largest == index:
                return

            # swap with larger child
            self._items[index], self._items[largest] = self._items[largest], self._items[index]
            index = largest