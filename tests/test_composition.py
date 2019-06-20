import unittest
from swpatterns.composition import Compose
from swpatterns.interface import Interface, implements, isimplementation

__all__ = ("TestCompose",)


class TestCompose(unittest.TestCase):
    def test_base(self):
        """Simple composition without forwarding or renaming with a single composite."""

        class A:
            ...

        class B(Compose(A)):
            ...

        b1 = B()
        self.assertEqual(type(b1._a), A)

        a = A()
        b2 = B(_a=a)
        self.assertEqual(b2._a, a)

    def test_multiple(self):
        """Simple composition without forwarding or renaming with multiple composites."""

        class A:
            ...

        class B:
            ...

        class C(Compose(A), Compose(B)):
            ...

        c1 = C()
        self.assertEqual(type(c1._a), A)
        self.assertEqual(type(c1._b), B)

        a = A()
        b = B()
        c2 = C(_a=a, _b=b)
        self.assertEqual(c2._a, a)
        self.assertEqual(c2._b, b)

    def test_rename(self):
        """Simple composition with renaming, but without forwarding."""

        class A:
            ...

        class B(Compose(A, name="a")):
            ...

        b = B()
        self.assertEqual(type(b.a), A)

    def test_forwarding_simple(self):
        """Simple composition with forwarding, but without renaming either the instance or the attibute."""

        class A:
            test = "123"

        class B(Compose(A, "test")):
            ...

        b = B()
        self.assertEqual(b.test, A.test)

    def test_forwarding_rename(self):
        """Simple composition with forwarding with renaming the attribute, but without renaming the instance."""

        class A:
            test = "123"

        class B(Compose(A, ("test", "var"))):
            ...

        b = B()
        self.assertEqual(b.var, A.test)

    def test_full(self):
        """Test all other things together."""

        class A:
            def __init__(self, val):
                self.test = val

        class B:
            def __init__(self, val):
                self.test = val

        class C(Compose(A, "test"), Compose(B, ("test", "test_b"), name="b_object")):
            ...

        a = A("123")
        b = B("456")
        c = C(_a=a, b_object=b)
        self.assertEqual(c.test + c.test_b, "123456")

    def test_nobuild(self):
        """Composition without automatic instance building."""

        class A:
            ...

        class B(Compose(A, build=False)):
            ...

        with self.assertRaises(ValueError):
            b1 = B()

        a = A()
        b2 = B(_a=a)
        self.assertEqual(b2._a, a)

    def test_autobuild(self):
        """Composition with automatic instance building and argument supplying."""

        class A:
            def __init__(self, x):
                self.x = x

        class B(Compose(A, "x", kwargs={"x": "123"})):
            ...

        b = B()
        self.assertEqual(b.x, "123")

    def test_interface(self):
        """Composition with interfaces"""

        class I(Interface):
            def test(self, a: int) -> int:
                ...

        @implements(I)
        class A:
            def test(self, a: int) -> int:
                return a + 1

        class B:
            def test(self, a: int) -> int:
                return a + 1

        class C(Compose(I, "test", name="obj")):
            ...

        a = A()
        c = C(obj=a)
        self.assertEqual(c.test(1), 2)

        with self.assertRaises(TypeError):
            b = B()
            c = B(obj=b)

