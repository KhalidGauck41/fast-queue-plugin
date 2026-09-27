import unittest

from priority_queue import PriorityQueue


class TestPushPop(unittest.TestCase):

    def test_empty_pop_raises(self):
        pq = PriorityQueue()
        with self.assertRaises(IndexError):
            pq.pop()

    def test_empty_peek_raises(self):
        pq = PriorityQueue()
        with self.assertRaises(IndexError):
            pq.peek()

    def test_single_item(self):
        pq = PriorityQueue()
        pq.push("a", 5)
        self.assertEqual(pq.pop(), ("a", 5))

    def test_pop_order_by_priority(self):
        pq = PriorityQueue()
        pq.push("a", 3)
        pq.push("b", 1)
        pq.push("c", 2)
        self.assertEqual(pq.pop(), ("b", 1))
        self.assertEqual(pq.pop(), ("c", 2))
        self.assertEqual(pq.pop(), ("a", 3))

    def test_peek_does_not_remove(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        pq.push("b", 0)
        self.assertEqual(pq.peek(), ("b", 0))
        self.assertEqual(len(pq), 2)
        self.assertEqual(pq.peek(), ("b", 0))

    def test_len_and_bool(self):
        pq = PriorityQueue()
        self.assertEqual(len(pq), 0)
        self.assertFalse(pq)
        pq.push("a", 1)
        self.assertEqual(len(pq), 1)
        self.assertTrue(pq)

    def test_contains(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        self.assertIn("a", pq)
        self.assertNotIn("b", pq)

    def test_duplicate_key_raises(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        with self.assertRaises(KeyError):
            pq.push("a", 2)

    def test_negative_priorities(self):
        pq = PriorityQueue()
        pq.push("a", -5)
        pq.push("b", -10)
        pq.push("c", 0)
        self.assertEqual(pq.pop(), ("b", -10))
        self.assertEqual(pq.pop(), ("a", -5))
        self.assertEqual(pq.pop(), ("c", 0))


class TestFifoTiebreak(unittest.TestCase):

    def test_equal_priorities_fifo(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        pq.push("b", 1)
        pq.push("c", 1)
        self.assertEqual(pq.pop(), ("a", 1))
        self.assertEqual(pq.pop(), ("b", 1))
        self.assertEqual(pq.pop(), ("c", 1))

    def test_fifo_after_decrease_key(self):
        # Two items at priority 5, then lower the second one to 1 and back to 5.
        # After lowering back, original insertion order should still hold for
        # ties because seq is never changed.
        pq = PriorityQueue()
        pq.push("a", 5)
        pq.push("b", 5)
        pq.decrease_key("b", 1)
        pq.decrease_key("a", 1)
        # Now both at priority 1; "b" was lowered first but "a" has lower seq.
        self.assertEqual(pq.pop(), ("a", 1))
        self.assertEqual(pq.pop(), ("b", 1))


class TestDecreaseKey(unittest.TestCase):

    def test_decrease_key_basic(self):
        pq = PriorityQueue()
        pq.push("a", 10)
        pq.push("b", 5)
        pq.decrease_key("a", 1)
        self.assertEqual(pq.pop(), ("a", 1))
        self.assertEqual(pq.pop(), ("b", 5))

    def test_decrease_key_to_same_raises(self):
        pq = PriorityQueue()
        pq.push("a", 5)
        with self.assertRaises(ValueError):
            pq.decrease_key("a", 5)

    def test_decrease_key_increase_raises(self):
        pq = PriorityQueue()
        pq.push("a", 5)
        with self.assertRaises(ValueError):
            pq.decrease_key("a", 6)

    def test_decrease_key_missing_raises(self):
        pq = PriorityQueue()
        with self.assertRaises(KeyError):
            pq.decrease_key("a", 1)

    def test_decrease_key_updates_get_priority(self):
        pq = PriorityQueue()
        pq.push("a", 10)
        pq.decrease_key("a", 3)
        self.assertEqual(pq.get_priority("a"), 3)

    def test_decrease_key_preserves_heap_property(self):
        pq = PriorityQueue()
        for i in range(10):
            pq.push(i, 100 - i)
        pq.decrease_key(9, -1)
        self.assertEqual(pq.peek(), (9, -1))
        prev = None
        while pq:
            key, pri = pq.pop()
            if prev is not None:
                self.assertLessEqual(prev, pri)
            prev = pri

    def test_decrease_key_on_root(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        pq.push("b", 5)
        pq.decrease_key("a", 0)
        self.assertEqual(pq.peek(), ("a", 0))

    def test_decrease_key_on_leaf(self):
        pq = PriorityQueue()
        pq.push("a", 1)
        pq.push("b", 5)
        pq.decrease_key("b", 0)
        self.assertEqual(pq.peek(), ("b", 0))


class TestGetPriority(unittest.TestCase):

    def test_get_priority_missing_raises(self):
        pq = PriorityQueue()
        with self.assertRaises(KeyError):
            pq.get_priority("a")

    def test_get_priority_after_push(self):
        pq = PriorityQueue()
        pq.push("a", 42)
        self.assertEqual(pq.get_priority("a"), 42)


class TestTypeValidation(unittest.TestCase):

    def test_push_non_int_priority(self):
        pq = PriorityQueue()
        with self.assertRaises(TypeError):
            pq.push("a", 1.5)

    def test_push_bool_priority_rejected(self):
        # bool is a subclass of int but is rejected to avoid silent surprises.
        pq = PriorityQueue()
        with self.assertRaises(TypeError):
            pq.push("a", True)

    def test_decrease_key_non_int_rejected(self):
        pq = PriorityQueue()
        pq.push("a", 5)
        with self.assertRaises(TypeError):
            pq.decrease_key("a", 2.0)


class TestIteration(unittest.TestCase):

    def test_iter_yields_keys(self):
        pq = PriorityQueue()
        pq.push("a", 3)
        pq.push("b", 1)
        keys = set(pq)
        self.assertEqual(keys, {"a", "b"})


class TestLargeSequence(unittest.TestCase):

    def test_random_push_decrease_pop(self):
        import random
        rng = random.Random(12345)
        pq = PriorityQueue()
        expected = []
        for i in range(200):
            pri = rng.randint(0, 1000)
            pq.push(i, pri)
            expected.append((i, pri))
        # Apply some decrease-key operations
        for _ in range(100):
            key = rng.randint(0, 199)
            cur = pq.get_priority(key)
            if cur > 0:
                new_pri = rng.randint(0, cur - 1)
                pq.decrease_key(key, new_pri)
                expected[key] = (key, new_pri)
        expected.sort(key=lambda x: (x[1], x[0]))
        for exp_key, exp_pri in expected:
            key, pri = pq.pop()
            self.assertEqual(key, exp_key)
            self.assertEqual(pri, exp_pri)
        self.assertEqual(len(pq), 0)


if __name__ == "__main__":
    unittest.main()
