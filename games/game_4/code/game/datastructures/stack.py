"""
stack.py - Stack data structure implementation

A Last-In-First-Out (LIFO) data structure.
The last item added is the first item removed (like a stack of plates).

Author: Kevin Le 
Date: 2/18/2026
Lab: Lab 4 - Time Travel with Stacks
"""
from datastructures.array import ArrayList

class Stack:
    """
    A LIFO (Last-In-First-Out) data structure.
    
    The last item added is the first item removed.
    Think of it like a stack of plates - you add to the top and remove from the top.
    """
    
    def __init__(self, capacity=180):
        """
        Initialize an empty stack.
        """
        self.items = ArrayList(capacity)  # Use ArrayList to store stack items
    
    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The item to add to the stack
        """
        self.items.append(item) 

    def is_full(self):
        """
        Check if the backing array has reached capacity.

        The time-travel feature uses this to behave like bounded history
        instead of crashing when the fixed custom array is full.
        """
        return self.items.size >= self.items.capacity

    def pop_oldest(self):
        """
        Remove and return the oldest item in the stack.

        This keeps the newest rewind states while preserving the custom
        Stack/ArrayList requirement.
        """
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The item that was on top of the stack, or None if empty
        """
        if self.is_empty():
            return None

        return self.items.pop()
        
    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The item on top of the stack, or None if empty
        """
        if self.is_empty():
            # Stack is empty, nothing to peek at
            return None  

        # Return the last item without removing it
        return self.items[self.items.size - 1]

    def is_empty(self):
        """
        Check if the stack is empty.
    
        Returns:
            bool: True if stack is empty, False otherwise
        """
        return self.items.size == 0


    def size(self):
        """
        Get the number of items in the stack.
    
        Returns:
            int: The number of items currently in the stack
        """
        return self.items.size
    
    def clear(self):
        """Remove all items from the stack."""
        self.items.clear()
    
    def __str__(self):
        """String representation of the stack (for debugging)."""
        return f"Stack({self.items})"
