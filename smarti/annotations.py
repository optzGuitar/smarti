from typing import Optional, Type
import smarti.class_loader as cl
import smarti.constants as cst

GLOBAL_CLASSLOADER = cl.ClassLoader()


def autowired(
    class_: Type = None,
    as_singleton: bool = False,
    class_loader: Optional[cl.ClassLoader] = None,
    **kwargs
):
    def decorator(decorated_class: Type):
        used_class_loader = GLOBAL_CLASSLOADER if class_loader is None else class_loader
        annotation_args = kwargs

        def __new__(cls, *args, **kwargs):
            if as_singleton:
                existing_instance = used_class_loader._instance_storage.get_instance(
                    decorated_class, args, kwargs
                )
                if existing_instance:
                    return existing_instance

            original_new = getattr(decorated_class, cst.UNMODIFIED_NEW)
            return original_new(cls)

        def __init__(self, **kwargs) -> None:
            existing_instance = used_class_loader._instance_storage.get_instance(
                decorated_class, [], kwargs
            )

            if not existing_instance:
                original_init = getattr(decorated_class, cst.UNMODIFIED_INIT)
                used_class_loader.autowire_function(
                    decorated_class,
                    original_init,
                    self,
                    as_singleton,
                    **{**annotation_args, **kwargs}
                )

                used_class_loader._instance_storage.add_or_get(
                    decorated_class, self, [], kwargs
                )

        setattr(decorated_class, cst.UNMODIFIED_INIT, decorated_class.__init__)
        setattr(decorated_class, cst.UNMODIFIED_NEW, decorated_class.__new__)
        decorated_class.__init__ = __init__
        decorated_class.__new__ = __new__

        dont_add = (
            kwargs[cst.DONT_ADD_TO_KNOWN] if cst.DONT_ADD_TO_KNOWN in kwargs else False
        )

        if not dont_add:
            used_class_loader._check_autowire._known_types.append(decorated_class)

        return decorated_class

    if class_ is None:
        return decorator
    else:
        return decorator(class_)
