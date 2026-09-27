# priority_queue

A binary min-heap that supports `decrease_key` in O(log n) without rebuilding the structure.

## Usage

```python
from priority_queue import PriorityQueue

pq = PriorityQueue()
pq.push("a", 5)
pq.push("b", 1)
pq.push("c", 3)

pq.decrease_key("a", 0)

print(pq.pop())  # ("a", 0)
print(pq.pop())  # ("b", 1)
print(pq.pop())  # ("c", 3)
```

## Why this exists

Dijkstra's shortest-path and Prim's MST algorithm both need to lower the priority
of an item already in the queue. A plain `heapq`-based heap has no way to do this
without scanning the array linearly or rebuilding the heap. This library keeps a
dictionary mapping each key to its array index, so `decrease_key` finds the node
in O(1) and bubbles it up in O(log n).

The trade-off: every key must be hashable and unique, and the queue carries an
extra dict whose size grows with the number of items. Memory overhead is roughly
two pointers per entry on top of the heap array itself.

## Edge cases

- `decrease_key` only lowers priorities. Calling it with a value that is greater
  than or equal to the current priority raises `ValueError`. This is deliberate:
  the common use case only ever decreases, and rejecting increases catches caller
  mistakes early.
- Priorities must be `int`. `bool` is rejected even though it is a subclass of
  `int`, because `True` and `1` being interchangeable in a priority queue is a
  source of silent bugs.
- Items with equal priority are popped in insertion order (FIFO). This holds even
  after `decrease_key` operations, because the internal insertion counter is set
  once at push time and never changed.
- Re-inserting an existing key raises `KeyError`. Use `decrease_key` instead.

## Exported names

- `PriorityQueue` — the only public class.

Methods: `push(key, priority)`, `pop()`, `peek()`, `decrease_key(key, new_priority)`,
`get_priority(key)`, plus `__len__`, `__bool__`, `__contains__`, and `__iter__`.

## Running tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
