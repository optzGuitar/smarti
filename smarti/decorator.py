from typing import Optional, Type, TypeVar
import smarti.class_loader as cl
import smarti.constants as cst

GLOBAL_CLASSLOADER = cl.ClassLoader()
T = TypeVar("T")


def autowired(
    class_: Type[T] = None,
    as_singleton: bool = True,
    class_loader: Optional[cl.ClassLoader] = None,
    **kwargs
):
    """The main decorator of this package. It allows to autowire classes by decorating them. It also supports singletons and custom class loader!
    If positional arguments are present, the whole autowireing is skipped to enable backwards compatability.

    Args:
        class_ (Type[T], optional): The class, typically inserted by python itself using the decorator syntax. Defaults to None.
        as_singleton (bool, optional): True if this class should be loaded as a singleton, False otherwise. Defaults to True.
        class_loader (Optional[cl.ClassLoader], optional): The custom class loader. If None smarti.decorator.GLOBAL_CLASSLOADER will be used. Defaults to None.
    """
    def decorator(decorated_class: Type[T]):
        used_class_loader = GLOBAL_CLASSLOADER if class_loader is None else class_loader
        annotation_args = kwargs

        def __new__(cls, *args, **kwargs) -> T:
            if as_singleton:
                existing_instance = used_class_loader._instance_storage.get_instance(
                    decorated_class, list(args), kwargs
                )
                if existing_instance:
                    return existing_instance

            original_new = getattr(decorated_class, cst.UNMODIFIED_NEW)
            return original_new(cls)

        def __init__(self, *args, **kwargs) -> None:
            if args:
                original_init = getattr(decorated_class, cst.UNMODIFIED_INIT)
                original_init(self, *args)
                return

            existing_instance = None
            if as_singleton:
                existing_instance = used_class_loader._instance_storage.get_instance(
                    decorated_class, [], kwargs
                )

            if not existing_instance:
                original_init = getattr(decorated_class, cst.UNMODIFIED_INIT)
                seen_types = kwargs.get(cst.ALREADY_SEEN_TYPES, [])
                used_class_loader.autowire_function(
                    decorated_class,
                    original_init,
                    self,
                    as_singleton,
                    seen_types,
                    **{**annotation_args, **kwargs}
                )

                used_class_loader._instance_storage.add_or_get(
                    decorated_class, self, [], kwargs
                )

        setattr(decorated_class, cst.UNMODIFIED_INIT, decorated_class.__init__)
        setattr(decorated_class, cst.UNMODIFIED_NEW, decorated_class.__new__)
        decorated_class.__init__ = __init__  # type: ignore
        decorated_class.__new__ = __new__  # type: ignore

        dont_add = (
            kwargs[cst.DONT_ADD_TO_KNOWN] if cst.DONT_ADD_TO_KNOWN in kwargs else False
        )

        if not dont_add:
            used_class_loader._check_autowire._known_types.append(
                decorated_class)

        return decorated_class

    if class_ is None:
        return decorator
    else:
        return decorator(class_)
