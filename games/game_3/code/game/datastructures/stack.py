"""
stack.py - Stack data structure implementation

A Last-In-First-Out (LIFO) data structure.
The last item added is the first item removed (like a stack of plates).

Author: [Mykai Wade]
Date: [2/20/26]
Lab: Lab 4 - Time Travel with Stacks
"""
from .array import ArrayList

class Stack:
    """
    Stack implementation using ArrayList as the underlying storage.
    
    Operations:
    - push: Add item to top - O(1) amortized
    - pop: Remove and return top item - O(1)
    - peek: View top item without removing - O(1)
    - is_empty: Check if stack is empty - O(1)
    - size: Get number of items - O(1)
    """
    
    def __init__(self):
        """
        Initialize an empty stack.
        
        Uses ArrayList internally to store elements.
        The end of the ArrayList represents the top of the stack.
        
        """
        self._data = ArrayList()
    
    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The element to add to the stack
        
        Example:
            stack = Stack()
            stack.push(10)
            stack.push(20)
            stack.size()
            2
        """
        self._data.append(item)
    
    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The top element, or None if the stack is empty
            
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.push(10)
            stack.push(20)
            20
            stack.pop()
            10
        """
        if self.is_empty():
            return None
        
        # pop() with no argument removes and returns the last element
        return self._data.pop()
    
    def peek(self):
        """
        Return the top item without removing it from the stack.
        
        Returns:
            The top element, or None if the stack is empty
            
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.push(10)
            stack.peek()
            10
            stack.size()  # Still has 1 element
            1
        """
        if self.is_empty():
            return None
        
        # Access the last element (top of stack)
        return self._data[len(self._data) - 1]
    
    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack has no elements, False otherwise
            
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.is_empty()
            True
            stack.push(1)
            stack.is_empty()
            False
        """
        return len(self._data) == 0
    
    def size(self):
        """
        Get the number of items in the stack.
        
        Returns:
            int: The number of elements currently in the stack
            
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.push(1)
            stack.push(2)
            stack.size()
            2
        """
        return len(self._data)
    
    def clear(self):
        """
        Remove all items from the stack.
        
        Time Complexity: O(n) where n is the number of elements
        
        Example:
            stack = Stack()
            stack.push(1)
            stack.push(2)
            stack.clear()
            stack.is_empty()
            True
        """
        self._data.clear()
    
    def __str__(self):
        """
        Return a string representation of the stack.
        Shows elements from bottom to top with an arrow indicating the top.
        
        Returns:
            str: String representation of the stack
            
        Example:
            stack = Stack()
            stack.push(1)
            stack.push(2)
            stack.push(3)
            print(stack)
            Stack: [1, 2, 3] <- top
        """
        if self.is_empty():
            return "Stack: [] (empty)"
        
        return f"Stack: {str(self._data)} <- top"


# End of file
