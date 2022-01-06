from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar
import inspect
from threading import Lock
from smarti import constants as cst

T = TypeVar("T")


class InstanceStorage:
    """This class handles all the singleton related magic.
    """
    IGNORED_ARGUMENTS = [cst.ALREADY_SEEN_TYPES]

    def __init__(self) -> None:
        self._storage: Dict[Tuple, Any] = {}
        self._storage_lock = Lock()

    def get_instance(
        self, type_: Type[T], arguments: List, kwargs: Optional[Dict] = None
    ) -> Optional[T]:
        """Get an existing instance or None from the storage.

        Args:
            type_ (Type[T]): The type of the instance.
            arguments (List): The arguments of the instance,
            kwargs (Optional[Dict], optional): The kwargs of the instance. Defaults to None.

        Raises:
            RuntimeError: If the module of the class cannot be found.

        Returns:
            Optional[T]: The instance of the type with the given arguments. None if there is no such instance.
        """
        classname = type_.__name__

        module = inspect.getmodule(type_)
        if module is None:
            raise RuntimeError(f"Could not get module of type {type_}")

        key = self._generate_key(
            module.__name__, classname, type_, arguments, kwargs)

        self._storage_lock.acquire()
        data = self._storage.get(key, None)
        self._storage_lock.release()

        return data

    def add_or_get(
        self, type_: Type[T], instance: T, arguments: List, kwargs: Optional[Dict] = None
    ) -> T:
        """Adds a new instance or gets the equal instance from the sotrage.

        Args:
            type_ (Type[T]): The class of the instance.
            instance (T): The instance itself.
            arguments (List): The arguments of the instance.
            kwargs (Optional[Dict], optional): The kwargs for the instance. Defaults to None.

        Raises:
            RuntimeError: If the module could not be found.

        Returns:
            T: The instance.
        """
        classname = type_.__name__
        module = inspect.getmodule(type_)
        if module is None:
            raise RuntimeError(f"Could not get module of type {type_}")

        key = self._generate_key(
            module.__name__, classname, type_, arguments, kwargs)

        self._storage_lock.acquire()
        data = self._storage.get(key, None)
        if data:
            self._storage_lock.release()
            return data

        self._storage[key] = instance
        self._storage_lock.release()

        return instance

    def _generate_key(
        self,
        module: str,
        classname: str,
        type_: Type,
        arguments: List,
        kwargs: Optional[Dict],
    ) -> Tuple:
        """Generates the key for the instance storage.

        Args:
            module (str): The module of the instance.
            classname (str): The classname of the instance.
            type_ (Type): The type of the instance,
            arguments (List): The arguments of the instance.
            kwargs (Optional[Dict]): The kwargs of the instance.

        Returns:
            Tuple: The key for the local instance storage.
        """
        extra = self.__convert_dict_to_tuples(kwargs) \
            if kwargs is not None else None
        sig = inspect.signature(type_.__init__)
        params = [i for i in sig.parameters.items() if i[0] != 'self']
        args = []

        for i, (name, param) in enumerate(params):
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                args.append((name, *arguments[i:]))
                continue
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                continue

            args.append((name, arguments[i]))

        key = tuple([f"{module}.{classname}", *args])
        if extra is not None:
            key += extra

        return key

    def __convert_dict_to_tuples(self, data: Dict) -> Tuple:
        """Converts a dict to tuples.

        Args:
            data (Dict): The dict to convert to tuples.

        Returns:
            Tuple: The converted dict.
        """
        converted = [
            (k, v if not isinstance(v, dict) else self.__convert_dict_to_tuples(v))
            for k, v in data.items() if k not in InstanceStorage.IGNORED_ARGUMENTS
        ]
        return converted[0] if len(converted) == 1 else tuple(converted)
