from __future__ import annotations

"""Low-level array skeleton.

TODO(ARRAY): Implement fixed-capacity storage without using Python's built-in
list as the core data structure. One option is ctypes.py_object arrays. Keep
this small and well-tested because other custom structures may depend on it.
"""

import ctypes

class Array:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity: int = capacity
        self._size: int = 0

        self._data = (ctypes.py_object * capacity)()
       
# Core interface

    def __len__(self) -> int:

        return self._size

    def get(self, index: int) -> object:
        self._check_index(index)
        return self._data[index]

       
    def set(self, index: int, value: object) -> None:
       self._check_index(index)
       self._data[index] = value

    def append(self, value: object) -> None:
        if self._size == self.capacity:
            self.resize(self.capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def resize(self, new_capacity: int) -> None:
        if new_capacity < self._size:
            raise ValueError(
                f"new_capacity ({new_capacity}) is smaller that"
                f"current size ({self._size})"
                
              )
        new_data = (ctypes.py_object * new_capacity)()
        # Copy existing elements into new buffer.
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self.capacity = new_capacity

# Heplers

     def _check_index(self, index: int) -> None:
         if not (0 <= index < self._size):
             raise IndexError(
            f"index {index} is out of range for array of size {self._size}"

             )
     def to_list(self) -> list:
         return [self._data[i] for i in range(self._size)]

     def __repr__(self): -> str # testing convenience
        return f"Array(size={self._size}, capacity={self.capacity}, data=[self.to_list()})"

# end of file 
    
    
