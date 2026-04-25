"""Algorithm tests sorting/search layer."""

import unittest

from algorithms import case_insensitive_contains, heap_sort, heapsort, merge_sort, mergesort, top_n


class TestAlgorithms(unittest.TestCase):
    def test_merge_sort_numbers_dicts_and_reverse(self) -> None:
        '''test merge sort with numbers, dictionaries, reverse order, and ties'''

        # sort simple numbers ascending
        self.assertEqual(merge_sort([3, 1, 2]), [1, 2, 3])

        # sort dictionary rows by score
        rows = [{"score": 20}, {"score": 10}, {"score": 20}]
        self.assertEqual(mergesort(rows, key=lambda row: row["score"]), [{"score": 10}, {"score": 20}, {"score": 20}])

        # sort numbers descending
        self.assertEqual(merge_sort([3, 1, 2], reverse=True), [3, 2, 1])

        # verify stable ordering for tied scores
        tied = [{"name": "first", "score": 20}, {"name": "second", "score": 20}, {"name": "third", "score": 10}]
        self.assertEqual(
            [row["name"] for row in mergesort(tied, key=lambda row: row["score"], reverse=True)],
            ["first", "second", "third"]
        )

    def test_heap_sort_and_contains_search(self) -> None:
        '''test heap sort, top_n, and case-insensitive contains search'''

        # sort simple numbers ascending
        self.assertEqual(heap_sort([3, 1, 2]), [1, 2, 3])

        # sort simple numbers descending
        self.assertEqual(heapsort([3, 1, 2], reverse=True), [3, 2, 1])

        # get top two players by score
        players = [{"username": "joy", "score": 50}, {"username": "hamza", "score": 80}, {"username": "kevin", "score": 65}]
        self.assertEqual([row["username"] for row in top_n(players, 2, key=lambda row: row["score"])], ["hamza", "kevin"])

        # search usernames without case sensitivity
        rows = [{"username": "JoyLead"}, {"username": "mykai"}]
        self.assertEqual(case_insensitive_contains(rows, "joy", lambda row: row["username"]), [{"username": "JoyLead"}])


if __name__ == "__main__":
    # run tests when file is executed directly
    unittest.main()