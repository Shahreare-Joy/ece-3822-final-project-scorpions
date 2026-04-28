"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Kevin Le 
Date: 2/10/2026
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        Initializes the dynamic array with a given initial capacity (default is 10).
        """

        self.capacity = initial_capacity
        self.size = 0
        self.data = [None] * self.capacity
        
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        returns the number of elements in the array
        """
        return self.size
        
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        returns the element at the specified index
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")
        return self.data[index]
        
    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        sets the element at the specified index to the given value
        """
        # TODO: Set element at index
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds") 
        self.data[index] = value
        
        
    def append(self, value):
        """
        appends a value to the end of the array, resizing if necessary
        """
        if self.size >= self.capacity:
            raise OverflowError("Array capacity is full, cannot append")

        self.data[self.size] = value
        self.size += 1
        
    
    def insert(self, index, value):
        """
        inserts a value at the specified index, shifting elements to the right
        """
        if self.size >= self.capacity:
            raise OverflowError("Array capacity is full, cannot insert")

        # Ensure there's space for the new element
        if index < 0 or index > self.size - 1:
            raise IndexError("Index out of bounds")

        # Shift elements to the right
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
            
        self.data[index] = value
        self.size += 1   
    
    def remove(self, value):
        """
        removes the first occurrence of the specified value, shifting elements to the left
        """
        idx = self.index(value)
        self.pop(idx)
            
    
    def pop(self, index=-1):
        """
        pops and returns the element at the specified index (default is the last element), shifting elements to the left
        """
        if self.size == 0:
            raise IndexError("Pop from empty list")

        if index == -1:
            index = self.size - 1

        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")

        removed_value = self.data[index]

        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.data[self.size - 1] = None
        self.size -= 1
        return removed_value    
    
    def clear(self):
        """
        clears all elements from the array, resetting size to 0 but keeping capacity the same
        """
        self.size = 0
        self.data = [None] * self.capacity  
    
    def index(self, value):
        """
        int returns the index of the first occurrence of the specified value, or raises ValueError if not found
        """
        for i in range(self.size):
            if self.data[i] == value:
                return i
        raise ValueError(f"{value} not found in array")


    def count(self, value):
        """
        counts and returns the number of occurrences of the specified value in the array
        """
        count = 0
        for i in range(self.size):
            if self.data[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        extends the array by appending elements from the given iterable 
        """
        for item in iterable:
            self.append(item)

    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        returns True if the specified value is in the array, False otherwise
        """
        for i in range(self.size):
            if self.data[i] == value:
                return True
        return False       
   
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        returns a user-friendly string representation of the array
        """
        return str(self.data[:self.size])
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        returns a developer-friendly string representation of the array
        """
        return f"ArrayList({self.data[:self.size]})"
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        returns an iterator for the array
        """
        self._iter_index = 0
        return self

    def __next__(self):
        """
        returns the next element in the iteration
        """
        if self._iter_index >= self.size:
            raise StopIteration
            
        value = self.data[self._iter_index]
        self._iter_index += 1
        return value