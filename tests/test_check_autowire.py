from abc import ABC, abstractmethod
from smarti.check_autowire import CheckAutowire
from smarti.class_loader_flags import ClassLoaderFlags
import pytest

from smarti.exceptions import CyclicDependencyException


class B:
    pass


class Y:
    def __init__(self, b: B) -> None:
        pass


class A(ABC):
    @abstractmethod
    def bla(self):
        pass


def dummyA():
    pass


def dummyB(b: B):
    pass


def dummyC(a):
    pass


def dummyD(a=""):
    pass


def dummyE(self, *args, **kwargs):
    pass


def dummyF(args, kwargs):
    pass


def test_can_autowire_function_non_threading():
    checker = CheckAutowire()
    flags = ClassLoaderFlags.NO_FLAGS

    assert checker.can_autowire(dummyA, flags, B, [], {})
    assert checker.can_autowire(dummyB, flags, B, [], {})
    assert not checker.can_autowire(dummyC, flags, B, [], {})
    assert checker.can_autowire(dummyD, flags, B, [], {})


def test_can_autowire_function_threading():
    class Y:
        pass

    checker = CheckAutowire()
    flags = ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED

    assert not checker.can_autowire(Y.__init__, flags, Y, [], {})
    checker._known_types.append(Y)
    assert checker.can_autowire(Y.__init__, flags, Y, [], {})


def test_can_autowire_type():
    checker = CheckAutowire()

    assert not checker.can_autowire_type(str)
    assert checker.can_autowire_type(B)
    assert not checker.can_autowire_type(A)


def test_is_thread_save():
    checker = CheckAutowire()
    flags = ClassLoaderFlags.NO_FLAGS

    assert not checker.is_thread_safe(flags)
    assert checker.is_thread_safe(ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED)
    assert checker.is_thread_safe(
        ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS)
    assert not checker.is_thread_safe(
        ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
        & ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS
    )


def test_is_autowired():
    checker = CheckAutowire()

    assert not checker.is_autowired(A)
    checker._known_types.append(A)
    assert checker.is_autowired(A)


def test_is_thread_safe():
    checker = CheckAutowire()

    assert not checker.is_thread_safe(ClassLoaderFlags.NO_FLAGS)
    assert checker.is_thread_safe(ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED)
    assert checker.is_thread_safe(
        ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS)
    assert checker.is_thread_safe(
        ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
        | ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS
    )


def test_is_autowired_or_ignored():
    checker = CheckAutowire()

    assert checker.is_autowired_or_ignored(A, ClassLoaderFlags.NO_FLAGS)
    assert not checker.is_autowired_or_ignored(
        A, ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
    )
    assert checker.is_autowired_or_ignored(
        A, ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS
    )
    checker._known_types.append(A)
    assert checker.is_autowired_or_ignored(
        A, ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
    )


def test_correctly_ignores_special_arguments():
    checker = CheckAutowire()

    assert checker.can_autowire(dummyE, ClassLoaderFlags.NO_FLAGS, B, [], {})
    assert not checker.can_autowire(
        dummyF, ClassLoaderFlags.NO_FLAGS, B, [], {})


def test_cyclic_dependency_check():
    checker = CheckAutowire()

    with pytest.raises(CyclicDependencyException):
        checker.can_autowire(Y.__init__, ClassLoaderFlags.NO_FLAGS, Y, [B], {})

    checker.can_autowire(
        Y.__init__, ClassLoaderFlags.NO_FLAGS, Y, [B], {'b': 'bla'})
