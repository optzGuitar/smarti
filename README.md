# Smarti - Smart Dependency Injection for Python

Just add the `@autowired` decorator to the class you want to autoload. To customize the loaded arguments (e.g., input specific enum value, with the argument name `number`) add it to the decorator like so `@autowire(number=Enum.one)`.

Furthermore, you can override/pass down arguments recursively using `name_kwargs`. This will use the given parameters to initialize `name`.

All of the described ways to modify the used arguments are also applicable when initializing the class. This means that you could call an autoloaded class using `A(a=4, b_kwargs={'x' = 3})` to modify local usage. These override the corresponding defaults of the decorator of `class A`.

When using singletons, different parameters will yield different instances, but the same will yield the same.

Everything is thread-safe when the `ClassLoaderFlags.ALL_DEPENDENCIES_AUTOWIRED` is specified. Additionally, this forces you to decorate the whole dependency tree. When using this flag, non-autowired classes raise a `RuntimeError`. To avoid such errors, use `ClassLoaderFlags.IGNORE_POSSIBLE_THREAD_ERRORS`, but it is not recommended. 

Installs via pip:
```
pip install smarti
```
