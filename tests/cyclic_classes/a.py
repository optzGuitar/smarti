class A:
    import tests.cyclic_classes.b as b

    def __init__(self, b: b.B) -> None:
        pass
