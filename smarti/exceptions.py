class CyclicDependencyException(Exception):
    """Represents a cyclic dependency. E.g. A -> B -> A.
    """
    pass
