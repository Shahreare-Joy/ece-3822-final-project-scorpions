"""
array_list.py - Custom Dynamic Array

This file contains an implementation of a dynamic array structure
that behaves similarly to Python's built-in list. The structure
automatically increases its storage capacity when needed.

Author: Hamza Mughal
Date: 2/10/26
Lab: Lab 3 - ArrayList and Inventory System
"""


class ArrayList:
    """
    A manually implemented resizable array.

    The structure stores elements in a fixed-size internal array
    and expands its capacity when it becomes full.
    """

    def __init__(self, initial_capacity=10):
        """Create a new ArrayList with optional initial capacity"""
        self._capacity = initial_capacity
        self._size = 0
        self._data = [None] * self._capacity

    def get_capacity(self):
        """Return the current capacity of the ArrayList"""
        return self._capacity

    def __len__(self):
        """Return the current number of stored elements"""
        return self._size

    def __getitem__(self, index):
        """Enable bracket access: arr[index]"""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        return self._data[index]

    def __setitem__(self, index, value):
        """Enable bracket assignment: arr[index] = value"""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Assignment index out of bounds")
        self._data[index] = value

    # Added methods to match test file
    def get(self, index):
        """Return the element at a given index"""
        return self.__getitem__(index)

    def set(self, index, value):
        """Set the element at a given index"""
        self.__setitem__(index, value)

    def _resize(self):
        """Double the internal storage capacity"""
        self._capacity *= 2
        new_storage = [None] * self._capacity
        for i in range(self._size):
            new_storage[i] = self._data[i]
        self._data = new_storage

    def append(self, value):
        """Add a new element to the end of the array"""
        if self._size == self._capacity:
            self._resize()
        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """Insert an element at a specific position"""
        if index < 0:
            index += self._size
        if index < 0:
            index = 0
        if index > self._size:
            index = self._size
        if self._size == self._capacity:
            self._resize()
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def remove(self, value):
        """Delete the first matching element found in the array"""
        for i in range(self._size):
            if self._data[i] == value:
                for j in range(i, self._size - 1):
                    self._data[j] = self._data[j + 1]
                self._data[self._size - 1] = None
                self._size -= 1
                return
        raise ValueError("Value does not exist in ArrayList")

    def pop(self, index=-1):
        """Remove and return the element at a given position"""
        if self._size == 0:
            raise IndexError("Cannot pop from empty ArrayList")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Pop index out of bounds")
        removed_value = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None
        self._size -= 1
        return removed_value

    def clear(self):
        """Remove every element while keeping allocated capacity"""
        self._data = [None] * self._capacity
        self._size = 0

    def index(self, value):
        """Return the position of the first occurrence of value"""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError("Value not found")

    def count(self, value):
        """Count how many times a value appears in the array"""
        occurrences = 0
        for i in range(self._size):
            if self._data[i] == value:
                occurrences += 1
        return occurrences

    def extend(self, iterable):
        """Add multiple elements from another iterable object"""
        for element in iterable:
            self.append(element)

    def __contains__(self, value):
        """Allow use of the 'in' keyword to check membership"""
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False

    def __str__(self):
        """Return a readable string version of the ArrayList"""
        elements = [str(self._data[i]) for i in range(self._size)]
        return "[" + ", ".join(elements) + "]"

    def __repr__(self):
        """Return the formal representation used in debugging"""
        return self.__str__()

    def __iter__(self):
        """Make the ArrayList iterable so it can be used in loops"""
        for i in range(self._size):
            yield self._data[i]

