"""Binary min-heap with O(log n) decrease-key via a position index.

The heap stores arbitrary items alongside integer priorities. Each item is
identified by a caller-chosen key (any hashable). A dictionary maps each key
to its current index in the heap array so that decrease_key can locate the
node in O(1) and bubble it up in O(log n), without rebuilding the structure.

Design decisions
----------------
* Keys must be hashable and unique. Re-inserting an existing key raises
  KeyError; use decrease_key instead. This keeps the two operations distinct
  and surfaces caller bugs immediately.
* Priorities are integers. Comparing arbitrary objects with < works in Python,
  but restricting to int makes the contract explicit and avoids surprises with
  mixed-type comparisons.
* When two items share a priority, pop returns whichever was inserted first
  (FIFO among equal priorities). This is achieved with a monotonically
  increasing insertion counter used as a tie-breaker, so ordering is stable
  and deterministic regardless of heap mutations.
"""

from __future__ import annotations

from typing import Any, Hashable, Iterator


class _Entry:
    __slots__ = ("key", "priority", "seq")

    def __init__(self, key: Hashable, priority: int, seq: int) -> None:
        self.key = key
        self.priority = priority
        self.seq = seq


class PriorityQueue:
    """A min-heap supporting efficient decrease-key.

    Items are inserted with an integer priority and popped in ascending priority
    order. Ties are broken by insertion order: among items with equal priority,
    the one inserted earliest comes out first. decrease_key lowers an existing
    item's priority in O(log n) time without rebuilding the heap.
    """

    def __init__(self) -> None:
        self._heap: list[_Entry] = []
        self._index: dict[Hashable, int] = {}
        self._counter: int = 0

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)

    def __contains__(self, key: object) -> bool:
        return key in self._index

    def __iter__(self) -> Iterator[Hashable]:
        # Iterate keys in current heap order. Not sorted by priority.
        return (entry.key for entry in self._heap)

    def push(self, key: Hashable, priority: int) -> None:
        """Insert a new item.

        Raises KeyError if the key already exists; call decrease_key instead.
        Raises TypeError if priority is not an int.
        """
        if key in self._index:
            raise KeyError(f"key already exists: {key!r}")
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise TypeError("priority must be an int")
        entry = _Entry(key, priority, self._counter)
        self._counter += 1
        self._heap.append(entry)
        pos = len(self._heap) - 1
        self._index[key] = pos
        self._sift_up(pos)

    def pop(self) -> tuple[Hashable, int]:
        """Remove and return the (key, priority) with the smallest priority.

        Raises IndexError if empty.
        """
        if not self._heap:
            raise IndexError("pop from an empty priority queue")
        top = self._heap[0]
        last = self._heap.pop()
        del self._index[top.key]
        if self._heap:
            self._heap[0] = last
            self._index[last.key] = 0
            self._sift_down(0)
        return top.key, top.priority

    def peek(self) -> tuple[Hashable, int]:
        """Return the (key, priority) with the smallest priority without removing it.

        Raises IndexError if empty.
        """
        if not self._heap:
            raise IndexError("peek at an empty priority queue")
        top = self._heap[0]
        return top.key, top.priority

    def decrease_key(self, key: Hashable, new_priority: int) -> None:
        """Lower the priority of an existing item.

        Raises KeyError if the key is not present.
        Raises ValueError if new_priority is not lower than the current one.
        Raises TypeError if new_priority is not an int.

        Only lowering is allowed. Raising a priority would require sifting down,
        which is straightforward to add but is deliberately omitted: the common
        use case (Dijkstra, Prim) only ever decreases, and rejecting increases
        catches caller mistakes early.
        """
        if key not in self._index:
            raise KeyError(f"key not found: {key!r}")
        if not isinstance(new_priority, int) or isinstance(new_priority, bool):
            raise TypeError("new_priority must be an int")
        pos = self._index[key]
        entry = self._heap[pos]
        if new_priority >= entry.priority:
            raise ValueError(
                f"new_priority {new_priority} is not lower than "
                f"current priority {entry.priority}"
            )
        entry.priority = new_priority
        self._sift_up(pos)

    def get_priority(self, key: Hashable) -> int:
        """Return the current priority of an item.

        Raises KeyError if the key is not present.
        """
        if key not in self._index:
            raise KeyError(f"key not found: {key!r}")
        return self._heap[self._index[key]].priority

    def _sift_up(self, pos: int) -> None:
        heap = self._heap
        index = self._index
        entry = heap[pos]
        while pos > 0:
            parent_pos = (pos - 1) >> 1
            parent = heap[parent_pos]
            if self._less(entry, parent):
                heap[pos] = parent
                index[parent.key] = pos
                pos = parent_pos
            else:
                break
        heap[pos] = entry
        index[entry.key] = pos

    def _sift_down(self, pos: int) -> None:
        heap = self._heap
        index = self._index
        n = len(heap)
        entry = heap[pos]
        while True:
            left = 2 * pos + 1
            if left >= n:
                break
            right = left + 1
            best = left
            if right < n and self._less(heap[right], heap[left]):
                best = right
            if self._less(heap[best], entry):
                heap[pos] = heap[best]
                index[heap[best].key] = pos
                pos = best
            else:
                break
        heap[pos] = entry
        index[entry.key] = pos

    @staticmethod
    def _less(a: _Entry, b: _Entry) -> bool:
        # Compare by priority first, then by insertion sequence for FIFO ties.
        if a.priority != b.priority:
            return a.priority < b.priority
        return a.seq < b.seq
