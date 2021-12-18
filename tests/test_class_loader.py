from smarti import autowired
from smarti.class_loader import ClassLoader
from smarti.class_loader_flags import ClassLoaderFlags
import pytest

multithread_classloader = ClassLoader(
    ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED)


class A:
    pass


@autowired(as_singleton=False)
class Y:
    pass


@autowired(as_singleton=True)
class AS:
    def __init__(self) -> None:
        pass


@autowired
class B:
    def __init__(self, a: A) -> None:
        self.a = a


@autowired
class C:
    def __init__(self, a1: Y, a2: Y) -> None:
        self.a1 = a1
        self.a2 = a2


@autowired(as_singleton=True)
class CS:
    def __init__(self, a1: AS, a2: AS) -> None:
        self.a1 = a1
        self.a2 = a2


@autowired
class D:
    def __init__(self, a1: A, a2: A) -> None:
        self.a1 = a1
        self.a2 = a2


class F:
    def __init__(self, a: str) -> None:
        self.a = a


@autowired(a=1, f_kwargs={"a": "123"})
class E:
    def __init__(self, a: int, f: F) -> None:
        self.a = a
        self.b = f


@autowired(as_singleton=True, c="abc")
class G:
    def __init__(self, c: str) -> None:
        self.c = c


@autowired
class H:
    def __init__(self, a: G) -> None:
        self.a = a


@autowired(class_loader=multithread_classloader)
class X:
    def __init__(self, a: A) -> None:
        self.a = A


@autowired
class J:
    def __init__(self, g: G) -> None:
        self.g = g


@autowired
class K:
    def __init__(self, s: str = "123") -> None:
        self.s = s


def dummyA():
    pass


def test_correctly_injects_non_singleton():
    instance = B()

    assert instance.a
    assert isinstance(instance.a, A)

    instance = C()

    assert instance.a1 is not instance.a2
    assert isinstance(instance.a1, Y)
    assert isinstance(instance.a2, Y)


def test_correctly_injects_singletons():
    instance = CS()

    assert instance.a1 is instance.a2
    assert isinstance(instance.a1, AS)


def test_correctly_injects_custom_attributes():
    instance = E()

    assert instance.a == 1
    assert instance.b.a == "123"


def test_correctly_override_defaults():
    instance = E(a=2, f_kwargs={"a": "321"})

    assert instance.a == 2
    assert instance.b.a == "321"


def test_correctly_override_defaults_autowired():
    instance = J(g_kwargs={"c": "123"})

    assert instance.g.c == "123"


def test_singletons_are_argument_sensitive():
    instance = G()
    instance2 = G(c="321")
    instance3 = G()

    assert instance.c == "abc"
    assert instance2.c == "321"
    assert instance is not instance2
    assert instance2 is not instance3
    assert instance is instance3


def test_can_load_autowired_class():
    instance = H()

    assert instance.a.c == "abc"


def test_cannot_load_not_autowired_class_when_threading():
    threw = False
    try:
        X()
    except RuntimeError:
        threw = True

    assert threw


def test_can_load_default_args():
    instance = K()

    assert instance.s == "123"


def test_throws_on_cyclic_dependencies():
    import tests.cyclic_classes.a as cca
    with pytest.raises(TypeError):
        cca.A()
