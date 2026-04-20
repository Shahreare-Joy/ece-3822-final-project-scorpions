"""
array.py - ArrayList implementation

Copy your completed implementation from Lab 3 into this file.
"""

# TODID: Copy your ArrayList implementation from Lab 3 here

"""
array.py - ArrayList implementation

Copy your completed implementation from Lab 3 into this file.
"""

"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Shahreare Joy
Date: 02/09/2026
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        Initialize an empty ArradyList with a given initial capacity.
        """
        # TODID: Initialize instance variables
        if initial_capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self._capacity = initial_capacity
        self._size = 0
        self._data = [None] * self._capacity
        
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        Return the number of elements in the ArrayList.
        """
        # TODID: Return the size
        return self._size
        
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        Return the element at the given index.
        """
        # TODID: Return element at index
        if not 0 <= index < self._size:
            raise IndexError("Index out of bounds")
        return self._data[index]
    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        Set the element at the given index value.
        """
        # TODID: Set element at index
        if not 0 <= index < self._size:
            raise IndexError("Index out of bounds")
        self._data[index] = value

    def _resize(self, new_capacity):
        """
        Resize the internal array to new_capacity.
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def get_capacity(self):
        """
        Return the current internal capacity of the ArrayList.
        """
        return self._capacity

    
    def append(self, value):
        """
        Add value to the end of the ArrayList.
        """
        if self._size == self._capacity:
            self._resize(2 * self._capacity)  # Double capacity if needed
          
        self._data[self._size] = value
        self._size += 1
    
    def insert(self, index, value):
        """
        Insert value at the given index.
        """
        if not 0 <= index <= self._size:
            raise IndexError("Index out of bounds")
        
        if self._size == self._capacity:
            self._resize(2 * self._capacity)  # Double capacity if needed
        
        # Shift elements to the right
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        
        self._data[index] = value
        self._size += 1
    
    def remove(self, value):
        """
        Remove the first occurrence of value.
        """
        idx = self.index(value)  # This will raise ValueError if not found
        self.pop(idx)
    
    def pop(self, index=-1):
        """
        Remove and return the element at index (default last).
        """
        if self._size == 0:
            raise IndexError("Pop from empty ArrayList")
        
        if index < 0:
            index += self._size
        
        if not 0 <= index < self._size:
            raise IndexError("Index out of bounds")
        
        value = self._data[index]

        # Shift elements to the left
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        
        self._data[self._size - 1] = None  # Help garbage collection
        self._size -= 1
        return value
    
    def clear(self):
        """
        Remove all elements from the ArrayList.
        """
        self._data = [None] * self._capacity
        self._size = 0
    
    def index(self, value):
        """
        Return the index of the first occurrence of value.
        """
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError("Value not found")

    def count(self, value):
        """
        Count occurrences of value in the ArrayList.
        """
        count = 0
        for i in range(self._size):
            if self._data[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        Append all elements from iterable.
        """
        for item in iterable:
            self.append(item)
    
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        Support the "in" operator.
        """
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        Return a user-friendly string representation.
        """
        return "[" + ", ".join(str(self._data[i]) for i in range(self._size)) + "]"
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        Return a developer-friendly representation.
        """
        return self.__str__()
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        Allow iteration over the ArrayList.
        """
        for i in range(self._size):
            yield self._data[i]

