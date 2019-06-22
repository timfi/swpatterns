import unittest
from swpatterns.matching import match, _

__all__ = ("TestMatching",)


class TestMatching(unittest.TestCase):
    def test_simple(self):
        """Simple matching."""

        res = match(1, _() >> 2)
        self.assertEqual(res, 2)

    def test_default(self):
        """Matching with default branch."""

        res = match(1, _.l(2) >> 2, _() >> 3)
        self.assertEqual(res, 3)

    def test_callable(self):
        """Matching with callable branch results."""

        res = match(1, _() >> (lambda: 1 + 1))
        self.assertEqual(res, 2)

    def test_branch_condition(self):
        """Matching with conditional branch."""

        res = match(1, _.c(lambda x: x % 2 == 1) >> (lambda x: x))
        self.assertEqual(res, 1)

    def test_branch_struct(self):
        """Matching with struct branch."""

        class A:
            def __init__(self, x, y=None):
                self.x = x
                self.y = y

        a1 = A(1)
        res = match(a1, _.s[A]("x") >> (lambda x: x))
        self.assertEqual(res, 1)
        res = match(a1, _.s[A]("y", x=1) >> (lambda y: y))
        self.assertEqual(res, None)
        res = match(a1, _.s[A]("y", x=lambda x: x % 2 == 1) >> (lambda y: y))
        self.assertEqual(res, None)
