

class B:
    import tests.cyclic_classes.c as c

    def __init__(self, c: c.C) -> None:
        pass
