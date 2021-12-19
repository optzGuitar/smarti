from __future__ import annotations
from smarti.annotations import autowired


@autowired
class A:
    def __init__(self, b: B) -> None:
        pass


class B:
    def __init__(self, c: C) -> None:
        pass


class C:
    def __init__(self, a: A) -> None:
        pass
