from __future__ import annotations
import tests.cyclic_classes.b as b
from smarti import autowired


@autowired
class A:

    def __init__(self, b: b.B) -> None:
        pass
