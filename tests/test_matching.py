import unittest
from swpatterns.matching import match, _

__all__ = ("TestMatching",)


class TestMatching(unittest.TestCase):
    def test_simple(self):
        """Simple matching."""

        res = match(1, _() >> 2)
        self.assertEqual(res, 2)

    def test_condition(self):
        """Matching with conditions."""

        res = match(1, _(cond=lambda x: x % 2 == 1) >> 2)
        self.assertEqual(res, 2)

    def test_default(self):
        """Matching with default branch."""

        res = match(1, _(2) >> 2, _() >> 3)
        self.assertEqual(res, 3)

    def test_callable(self):
        """Matching with callable branch results."""

        res = match(1, _() >> (lambda: 1 + 1))
        self.assertEqual(res, 2)
