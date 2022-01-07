import inspect
import smarti as sti
import smarti.constants as cst
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints, TypeVar

from smarti.check_autowire import CheckAutowire
from smarti.class_loader_flags import ClassLoaderFlags
from smarti.instance_storage import InstanceStorage

T = TypeVar('T')


class ClassLoader:
    """This classloader is responsible for instanciating the new instances. It automatically detects if a class is autowired or not and loads it correspondingly."""

    def __init__(self, flags: ClassLoaderFlags = ClassLoaderFlags.NO_FLAGS) -> None:
        self._check_autowire = CheckAutowire()
        self._instance_storage = InstanceStorage()

        self.set_flags(flags)

    def set_flags(self, flags: ClassLoaderFlags):
        """Updates the flags to this ClassLoader.

        Args:
            flags (ClassLoaderFlags): The new flags.
        """
        self._flags = flags

    def manually_add_instance(self, type_: Type[T], instance: T, arguments: List[Any], kwargs: Optional[Dict[str, Any]] = None) -> T:
        """Manually adds an instance to the instance storage. This has only an effect if singletons are used!

        Args:
            type_ (Type[T]): The type of the instance
            instance (T): The instance itself.
            arguments (List[Any]): The arguments needed to instantiate the instance.
            kwargs (Optional[Dict[str, Any]], optional): Custom KWargs of the instance. Defaults to None.

        Returns:
            T: The instance or an equal already saved instance.
        """
        return self._instance_storage.add_or_get(type_, instance, arguments, kwargs)

    def autowire_function(
        self,
        type_: Type,
        function: Callable,
        self_arg: Any,
        as_singleton: bool,
        seen_types: List[Type],
        **kwargs,
    ):
        """Autowired a callable.

        Args:
            type_ (Type): The type the callable belongs to.
            function (Callable): The callable itself.
            self_arg (Any): The self-arg of the callable.
            as_singleton (bool): True if singletons should be used, False otherwise.
            seen_types (List[Type]): The already instanciated types of this depencency chain.

        Raises:
            RuntimeError: If the function cannot be autowired.
            TypeError: If a type cannot be autowired.
            CyclicDependencyException: If there exists a cyclic dependency between types.
        """
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
        self, type: Type[T], name: str, kwargs: Dict[str, Any], as_singleton: bool, seen_types: List[Type]
    ) -> T:
        """Instantiate a class.

        Args:
            type (Type[T]): The type to instantiate
            name (str): Argument name for the kwargs
            kwargs (Dict[str, Any]): The kwargs.
            as_singleton (bool): True if singletons should be used, False otherwise.
            seen_types (List[Type]): The already instanciated types of this depencency chain.

        Returns:
            T: The new or stored instance of the type.
        """
        class_ = self._load_class_type(type)

        if self._check_autowire.is_autowired(class_):
            custom_args = self._get_kwargs_for_argument(name, kwargs)
            instance = self._create_instance(class_, custom_args, seen_types)
        else:
            instance = self._recursive_instantiate(
                class_, as_singleton, name, kwargs, seen_types)

        return instance

    def _recursive_instantiate(
        self, class_: Type[T], as_singleton: bool, name: str, kwargs: Dict[str, Any], seen_types: List[Type],
    ) -> T:
        """Recursively instantiates a class.

        Args:
            class_ (Type[T]): The class to instantiate
            as_singleton (bool): If singletons should be used.
            name (str): The name of the argument.
            kwargs (Dict[str, Any]): The kwargs.
            seen_types (List[Type]): The already instanciated types of this depencency chain.

        Raises:
            RuntimeError: If thread-safety is flagged and one of the classes of the dependency chain is not autowired.

        Returns:
            T: The instance.
        """
        custom_args = self._get_kwargs_for_argument(name, kwargs)

        # TODO: check if thread safety is an option; due to new decorator may be not possible anymore
        if self._check_autowire.is_thread_safe(self._flags):
            raise RuntimeError(
                f"Cannot create unwired class in {ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED} mode"
            )

        class_ = sti.autowired(
            class_, as_singleton, self, **{cst.DONT_ADD_TO_KNOWN: True}
        )
        instance = self._create_instance(class_, custom_args, seen_types)

        class_.__init__ = getattr(class_, cst.UNMODIFIED_INIT)  # type: ignore
        class_.__new__ = getattr(class_, cst.UNMODIFIED_NEW)  # type: ignore

        return instance

    def _create_instance(self, type_: Type[T], custom_args: Dict[str, Any], seen_types: List[Type]) -> T:
        try:
            return type_(
                **{**custom_args, cst.ALREADY_SEEN_TYPES: seen_types})  # type: ignore
        except TypeError as e:
            raise TypeError(f"Cannot create {type_} with custom args {custom_args} and dependency chain {seen_types}") from e

    def _load_class_type(self, type: Type) -> Any:
        """Gets the type of a type.

        Args:
            type (Type): The type to get the type from.

        Returns:
            Any: Sonething
        """
        module = inspect.getmodule(type)

        return getattr(module, type.__name__)

    def _get_kwargs_for_argument(
        self, name: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gets the custom args for the given argument.

        Args:
            name (str): The argument name.
            kwargs (Dict[str, Any]): All the kwargs.

        Returns:
            Dict[str, Any]: The kwargs for the given argument.
        """
        kwa = kwargs.get(f"{name}{cst.KWARGS_VALUE}", None)

        if not kwa:
            return {}

        return kwa
