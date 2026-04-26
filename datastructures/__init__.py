"""Custom data structures for the ECE 3822 assignment.

IMPORTANT: Final implementations in this package should be custom code. Avoid
using Python dict/list/set as the main internal storage unless the professor
explicitly allows it for a wrapper or test helper.
"""

from .array import Array
from .bst import BinarySearchTree
from .circular_buffer import CircularBuffer
from .graph import Edge, Graph
from .hash_table import ChainedHashTable
from .heap import MaxHeap
from .linked_list import LinkedList
from .linked_queue import LinkedQueue
from .linked_stack import LinkedStack

__all__ = [
    "Array",
    "BinarySearchTree",
    "ChainedHashTable",
    "CircularBuffer",
    "Edge",
    "Graph",
    "LinkedList",
    "LinkedQueue",
    "LinkedStack",
    "MaxHeap",
]
