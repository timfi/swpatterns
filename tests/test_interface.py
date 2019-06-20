import unittest
from swpatterns.interface import Interface, implements, isimplementation

__all__ = ("TestInterface",)


class TestInterface(unittest.TestCase):
    def test_simple(self):
        """Simple interface with implementation."""

        class I(Interface):
            def test(self, a):
                ...

        @implements(I)
        class A:
            def test(self, a):
                return a + 1

        self.assertTrue(isimplementation(A, I))

    def test_staticmethod(self):
        """Interface with staticmethod and implementation."""

        class I(Interface):
            @staticmethod
            def test(a):
                ...

        @implements(I)
        class A:
            @staticmethod
            def test(a):
                return a + 1

        self.assertTrue(isimplementation(A, I))

    def test_classmethod(self):
        """Interface with classmethod and implementation."""

        class I(Interface):
            @classmethod
            def test(cls, a):
                ...

        @implements(I)
        class A:
            @classmethod
            def test(cls, a):
                return a + 1

        self.assertTrue(isimplementation(A, I))

    def test_type(self):
        """Simple interface with implementation with type checking."""

        class I(Interface):
            def test(self, a: int) -> int:
                ...

        @implements(I)
        class A:
            def test(self, a: int) -> int:
                return a + 1

        self.assertTrue(isimplementation(A, I))

        with self.assertRaises(TypeError):

            @implements(I)
            class B:
                def test(self, a: str) -> str:
                    return a.lower()

        @implements(I, skip_types=True)
        class C:
            def test(self, a: str) -> str:
                return a.lower()

        self.assertTrue(isimplementation(C, I))

        @implements(I, skip_types=True)
        class D:
            def test(self, a):
                return a.lower()

        self.assertTrue(isimplementation(D, I))

    def test_partialtypes(self):
        """Simple interface with implementation with type checking without types."""

        class I(Interface):
            def test(self, a):
                ...

        @implements(I)
        class A:
            def test(self, a: int) -> int:
                return a + 1

        self.assertTrue(isimplementation(A, I))
