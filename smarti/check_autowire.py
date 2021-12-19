import builtins
import inspect
from typing import Callable, List, Type, get_type_hints, Any, Dict
import enum

from smarti.class_loader_flags import ClassLoaderFlags
from smarti.exceptions import CyclicDependencyException


class CheckAutowire:
    ANNOTATIONS_MODULE = "smarti.annotations"
    IGNORED_ARGUMENTS = ["self"]

    def __init__(self) -> None:
        self._known_types: List[Type] = []

    def can_autowire(
        self, callable: Callable, flags: ClassLoaderFlags, type_: Type, seen_types: List[Type], kwargs: Dict[str, Any]
    ) -> bool:
        hints = get_type_hints(callable)

        signature = inspect.signature(callable)

        for name, param_type in get_type_hints(callable).items():
            if param_type in seen_types and name not in kwargs:
                circle = [
                    t_.__name__ for t_ in seen_types[seen_types.index(param_type):] + [param_type]
                ]
                raise CyclicDependencyException(
                    f"Found cyclic dependencies: {' -> '.join(circle)}")

        problems = {
            k: v
            for k, v in signature.parameters.items()
            if k not in hints
            and k not in CheckAutowire.IGNORED_ARGUMENTS
            and v.kind
            not in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]
            and v.default is inspect.Parameter.empty
        }

        is_autowired = self.is_autowired_or_ignored(type_, flags)

        return not problems and is_autowired

    def can_autowire_type(self, type_: Type) -> bool:
        type_to_check = type_

        if type.__module__.endswith(CheckAutowire.ANNOTATIONS_MODULE):
            type_to_check = type_.__bases__[0]

        type_str = type_to_check.__name__

        return (
            type_str not in [name for name in dir(
                builtins) if name[0].islower()]
            and not inspect.isabstract(type_to_check)
            and not issubclass(type_to_check, enum.Enum)
        )

    def is_autowired_or_ignored(self, class_: Type, flags: ClassLoaderFlags) -> bool:
        is_autowired = self.is_autowired(class_)
        force_all_autowired = bool(
            flags & ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED)
        ignore = bool(flags & ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS)

        return is_autowired or not force_all_autowired or ignore

    def is_autowired(self, class_: Type) -> bool:
        return class_ in self._known_types

    def is_thread_safe(self, flags: ClassLoaderFlags) -> bool:
        return bool(
            flags & ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED
            or flags & ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS
        )
