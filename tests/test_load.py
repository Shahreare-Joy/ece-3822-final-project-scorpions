"""Large-load stress tests.

TODO(STRESS): Generate/load 10,000+ players and 100,000+ sessions, then time
search, leaderboard, history, and catalog operations.
"""

import unittest


class TestLoad(unittest.TestCase):
    @unittest.skip("TODO: implement synthetic dataset loader before enabling stress test.")
    def test_large_dataset_load(self) -> None:
        self.fail("Implement large dataset stress test.")
