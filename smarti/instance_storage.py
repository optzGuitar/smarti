from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar
import inspect
from threading import Lock

T = TypeVar("T")


class InstanceStorage:
    def __init__(self) -> None:
        self._storage: Dict[Tuple, Any] = {}
        self._storage_lock = Lock()

    def get_instance(
        self, type_: Type, arguments: List, kwargs: Optional[Dict] = None
    ) -> Optional[T]:
        classname = type_.__name__

        module = inspect.getmodule(type_)
        if module is None:
            raise RuntimeError(f"Could not get module of type {type_}")

        key = self._generate_key(module.__name__, classname, type_, arguments, kwargs)

        self._storage_lock.acquire()
        data = self._storage.get(key, None)
        self._storage_lock.release()

        return data

    def add_or_get(
        self, type_: Type, instance: T, arguments: List, kwargs: Optional[Dict] = None
    ) -> T:
        classname = type_.__name__
        module = inspect.getmodule(type_)
        if module is None:
            raise RuntimeError(f"Could not get module of type {type_}")

        key = self._generate_key(module.__name__, classname, type_, arguments, kwargs)

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
        extra = self.__convert_dict_to_tuples(kwargs) if kwargs is not None else None
        sig = inspect.signature(type_.__init__)
        names = [name for name in sig.parameters.keys() if not name == "self"]
        args = []

        for i, name in enumerate(names):
            if name == "args":
                args.append((name, *arguments[i:]))
                break
            elif name == "kwargs":
                continue

            args.append((name, arguments[i]))

        key = tuple([f"{module}.{classname}", *args])
        if extra is not None:
            key += extra

        return key

    def __convert_dict_to_tuples(self, data: Dict) -> Tuple:
        converted = [
            (k, v if not isinstance(v, dict) else self.__convert_dict_to_tuples(v))
            for k, v in data.items()
        ]
        return converted[0] if len(converted) == 1 else tuple(converted)
