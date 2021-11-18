import inspect
import smarti as sti
import smarti.constants as cst
from typing import Any, Callable, Dict, Type, get_type_hints

from smarti.check_autowire import CheckAutowire
from smarti.class_loader_flags import ClassLoaderFlags
from smarti.instance_storage import InstanceStorage


class ClassLoader:
    def __init__(self, flags: ClassLoaderFlags = ClassLoaderFlags.NO_FLAGS) -> None:
        self._check_autowire = CheckAutowire()
        self._instance_storage = InstanceStorage()

        self.set_flags(flags)

    def set_flags(self, flags: ClassLoaderFlags):
        self._flags = flags
        self._dont_replace_init = flags & ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
        self._dont_throw_thread_warnings = (
            flags & ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS
        )

    def autowire_function(
        self,
        type_: Type,
        function: Callable,
        self_arg: Any,
        as_singleton: bool,
        **kwargs,
    ):
        args = [self_arg]

        if not self._check_autowire.can_autowire(function, self._flags, type_):
            raise RuntimeError(f"Cannot Autowire function {function}")

        sign = inspect.signature(function)

        for name, type in get_type_hints(function).items():
            if name == "self" or name == "return":
                continue

            if name in kwargs:
                args.append(kwargs[name])
                continue

            if sign.parameters[name].default is not inspect.Parameter.empty:
                continue

            if not self._check_autowire.can_autowire_type(type):
                raise RuntimeError(f"Cannot Autowire {name}: {type} of {function}")

            args.append(self._instantiate_class(type, name, kwargs, as_singleton))

        function(*args)

    def _instantiate_class(
        self, type: Type, name: str, kwargs: Dict[str, Any], as_singleton: bool
    ) -> Any:
        class_ = self._load_class_type(type)

        if self._check_autowire.is_autowired(class_):
            custom_args = self._get_kwargs_for_argument(name, kwargs)
            instance = class_(**custom_args)
        else:
            instance = self._recursive_instantiate(class_, as_singleton, name, kwargs)

        return instance

    def _recursive_instantiate(
        self, class_: Type, as_singleton: bool, name: str, kwargs: Dict[str, Any]
    ) -> Any:
        custom_args = self._get_kwargs_for_argument(name, kwargs)

        # TODO: check if thread safety is an option; due to new decorator may be not possible anymore
        if self._check_autowire.is_thread_safe(self._flags):
            raise RuntimeError(
                f"Cannot create unwired class in {ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED} mode"
            )

        class_ = sti.autowired(
            class_, as_singleton, self, **{cst.DONT_ADD_TO_KNOWN: True}
        )
        instance = class_(**custom_args)

        class_.__init__ = getattr(class_, cst.UNMODIFIED_INIT)
        class_.__new__ = getattr(class_, cst.UNMODIFIED_NEW)

        return instance

    def _load_class_type(self, type: Type) -> Any:
        module = inspect.getmodule(type)

        return getattr(module, type.__name__)

    def _get_kwargs_for_argument(
        self, name: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        kwa = kwargs.get(f"{name}_kwargs", None)

        if not kwa:
            return {}

        return kwa

    def _init_has_no_arguments(self, class_: Type) -> bool:
        signature = inspect.signature(class_.__init__)
        relevant_args = [
            k
            for k, v in signature.parameters.items()
            if k not in CheckAutowire.IGNORED_ARGUMENTS
            and v.kind
            not in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]
        ]

        return len(relevant_args) == 0
