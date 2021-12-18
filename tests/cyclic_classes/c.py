

class C:
    import tests.cyclic_classes as a

    def __init__(self, a: a.A) -> None:
        pass
