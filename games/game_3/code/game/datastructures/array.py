"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: [Mykai Wade]
Date: [2/11/26]
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
         Initialize a new ArrayList with the specified capacity.
        
        Args:
            initial_capacity (int): The initial capacity of the array. Defaults to 10.
        Example:
        ArrayList() # Array defaults to 10 capacity
        ArrayList(5) # Array with capacity 5
        """

        self._capacity = initial_capacity
        self._size = 0
        self._data = [None] * self._capacity
        
    def get_capacity(self):
        """
        Return current capacity of Arraylist

        Returns the total number of slots avalable used and unused

        Example:
        arr = ArrayList(5)
        arr.get_capacity()
        5
        """

        return self._capacity
   
    
    def __len__(self):
        """
        Return the number of elements currently stored in the ArrayList.
        Enables the built-in len() function.
        
        Example:
            arr = ArrayList()
            arr.append(1)
            len(arr)
            1
        """
        return self._size
    
    def __getitem__(self, index):
        """
        Get the element at the specified index.
        Enables bracket notation for accessing elements.
        
        Args:
            index (int): The position to access (can be negative)
        Raises:
            IndexError: If the index is out of range
        Example:
            arr = ArrayList()
            arr.append(10)
            arr[0]
            10
        """
        # Handle negative indices
        if index < 0:
            index = self._size + index
        
        # Check bounds
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList index out of range")
        
        return self._data[index]
    
    def __setitem__(self, index, value):
        """
        Set the element at the specified index to a new value.
        Enables bracket notation for setting elements.
        
        Args:
            index (int): The position to modify (can be negative)
            value: The new value to store
        Raises:
            IndexError: If the index is out of range
        Example:
            arr = ArrayList()
            arr.append(1)
            arr[0] = 42
            arr[0]
            42
        """
        # Handle negative indices
        if index < 0:
            index = self._size + index
        
        # Check bounds
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList index out of range")
        
        self._data[index] = value
    
    def _resize(self, new_capacity):
        """
        Resize the underlying array to a new capacity.
        Private helper method that creates a new array and copies elements.
        
        Args:
            new_capacity (int): The new capacity for the array
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity
    
    def append(self, value):
        """
        Add an element to the end of the ArrayList.
        Automatically resizes to double capacity if full. O(1) amortized.
        
        Args:
            value: The element to add
        Example:
            arr = ArrayList()
            arr.append(10)
            arr.append(20)
            len(arr)
            2
        """
        # Resize if necessary
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        
        # Add the element
        self._data[self._size] = value
        self._size += 1
    
    def insert(self, index, value):
        """
        Insert an element at the specified position.
        Shifts all elements at and after index one position right. O(n).
        
        Args:
            index (int): The position to insert at
            value: The element to insert
        Raises:
            IndexError: If the index is out of range
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.append(3)
            arr.insert(1, 2)
            arr[1]
            2
        """
        # Handle negative indices
        if index < 0:
            index = self._size + index + 1
        
        # Check bounds (can insert at position size, which is end)
        if index < 0 or index > self._size:
            raise IndexError("ArrayList index out of range")
        
        # Resize if necessary
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        
        # Shift elements to the right
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        
        # Insert the new element
        self._data[index] = value
        self._size += 1
    
    def remove(self, value):
        """
        Remove the first occurrence of the specified value.
        Shifts all elements after the removed element one position left.
        
        Args:
            value: The value to remove
        Raises:
            ValueError: If the value is not found
        Example:
            arr = ArrayList()
            arr.append(10)
            arr.append(20)
            arr.remove(10)
            arr[0]
            20
        """
        # Find the index of the value
        for i in range(self._size):
            if self._data[i] == value:
                # Shift elements to the left
                for j in range(i, self._size - 1):
                    self._data[j] = self._data[j + 1]
                
                # Clear the last element and decrease size
                self._data[self._size - 1] = None
                self._size -= 1
                return
        
        # Value not found
        raise ValueError(f"{value} not in ArrayList")
    
    def pop(self, index=-1):
        """
        Remove and return the element at the specified index.
        If no index specified, removes and returns the last element.
        
        Args:
            index (int): The position to remove. Defaults to -1 (last element)
        Returns:
            The element that was removed
        Raises:
            IndexError: If the array is empty or index is out of range
        Example:
            arr = ArrayList()
            arr.append(10)
            arr.append(20)
            arr.pop()
            20
        """
        if self._size == 0:
            raise IndexError("pop from empty ArrayList")
        
        # Handle negative indices
        if index < 0:
            index = self._size + index
        
        # Check bounds
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList index out of range")
        
        # Get the value to return
        value = self._data[index]
        
        # Shift elements to the left
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        
        # Clear the last element and decrease size
        self._data[self._size - 1] = None
        self._size -= 1
        
        return value
    
    def clear(self):
        """
        Remove all elements from the ArrayList.
        Resets size to 0 but maintains current capacity.
        
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.clear()
            len(arr)
            0
        """
        for i in range(self._size):
            self._data[i] = None
        self._size = 0
    
    def index(self, value):
        """
        Return the index of the first occurrence of the specified value.
        
        Args:
            value: The value to search for
        Returns:
            int: The index of the first occurrence
        Raises:
            ValueError: If the value is not found
        Example:
            arr = ArrayList()
            arr.append(10)
            arr.append(20)
            arr.index(20)
            1
        """
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError(f"{value} is not in ArrayList")
    
    def count(self, value):
        """
        Return the number of times the specified value appears.
        
        Args:
            value: The value to count
        Returns:
            int: The number of occurrences
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.append(2)
            arr.append(1)
            arr.count(1)
            2
        """
        count = 0
        for i in range(self._size):
            if self._data[i] == value:
                count += 1
        return count
    
    def extend(self, iterable):
        """
        Extend the ArrayList by appending all elements from the iterable.
        
        Args:
            iterable: Any iterable whose elements will be appended
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.extend([2, 3, 4])
            len(arr)
            4
        """
        for item in iterable:
            self.append(item)
    
    def __contains__(self, value):
        """
        Check if the ArrayList contains the specified value.
        Enables the 'in' operator.
        
        Args:
            value: The value to search for
        Returns:
            bool: True if the value is in the array, False otherwise
        Example:
            arr = ArrayList()
            arr.append(10)
            10 in arr
            True
        """
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False
    
    def __str__(self):
        """
        Return a user-friendly string representation of the ArrayList.
        Called by str() and print().
        
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.append(2)
            print(arr)
            [1, 2]
        """
        if self._size == 0:
            return "[]"
        
        result = "["
        for i in range(self._size):
            result += str(self._data[i])
            if i < self._size - 1:
                result += ", "
        result += "]"
        return result
    
    def __repr__(self):
        """
        Return a developer-friendly string representation.
        Used in the interactive shell and for debugging.
        
        Example:
            arr = ArrayList()
            arr.append(1)
            arr
            ArrayList([1])
        """
        return f"ArrayList({str(self)})"
    
    def __iter__(self):
        """
        Return an iterator for the ArrayList.
        Enables for loops and other iteration constructs.
        
        Example:
            arr = ArrayList()
            arr.append(1)
            arr.append(2)
            for item in arr:
                print(item)
            1
            2
        """
        for i in range(self._size):
            yield self._data[i]

# end of file
