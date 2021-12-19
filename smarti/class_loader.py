import inspect
import smarti as sti
import smarti.constants as cst
from typing import Any, Callable, Dict, List, Type, get_type_hints

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
        seen_types: List[Type],
        **kwargs,
    ):
        args = [self_arg]

        sign = inspect.signature(function)
        if not self._check_autowire.can_autowire(function, self._flags, type_, seen_types, kwargs):
            raise RuntimeError(f"Cannot Autowire function {function}")

        for name, arg_type in get_type_hints(function).items():
            if name == "self" or name == "return":
                continue

            if name in kwargs:
                args.append(kwargs[name])
                continue

            if sign.parameters[name].default is not inspect.Parameter.empty:
                continue

            if not self._check_autowire.can_autowire_type(arg_type):
                raise TypeError(
                    f"Cannot Autowire {name}: {arg_type} of {function}")

            args.append(self._instantiate_class(
                arg_type, name, kwargs, as_singleton, [*seen_types, arg_type]))

        function(*args)

    def _instantiate_class(
        self, type: Type, name: str, kwargs: Dict[str, Any], as_singleton: bool, seen_types: List[Type]
    ) -> Any:
        class_ = self._load_class_type(type)

        if self._check_autowire.is_autowired(class_):
            custom_args = self._get_kwargs_for_argument(name, kwargs)
            instance = class_(
                **{**custom_args, cst.ALREADY_SEEN_TYPES: seen_types})
        else:
            instance = self._recursive_instantiate(
                class_, as_singleton, name, kwargs, seen_types)

        return instance

    def _recursive_instantiate(
        self, class_: Type, as_singleton: bool, name: str, kwargs: Dict[str, Any], seen_types: List[Type],
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
        instance = class_(
            **{**custom_args, cst.ALREADY_SEEN_TYPES: seen_types})

        class_.__init__ = getattr(class_, cst.UNMODIFIED_INIT)
        class_.__new__ = getattr(class_, cst.UNMODIFIED_NEW)

        return instance

    def _load_class_type(self, type: Type) -> Any:
        module = inspect.getmodule(type)

        return getattr(module, type.__name__)

    def _get_kwargs_for_argument(
        self, name: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        kwa = kwargs.get(f"{name}{cst.KWARGS_VALUE}", None)

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
