"""
HooksFF: Hooks for functions.

MIT License

Copyright (c) 2022 Koviubi56

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

>>> @mark_as_hookable("demo1")
... def add(a: int, b: int) -> int:
...     return a + b
>>> add(1, 2)
3
>>> @hook_for("demo1")
... def hook1(a: int, b: int) -> HookResponse:
...     return Change(a, b + 1)
>>> add(1, 2)
4
>>> isinstance(hooks, dict)
True
>>> isinstance(hooks["demo1"], list)
True
>>> callable(hooks["demo1"][0])
True
>>> remove_hooks_for("demo1")
>>> add(1, 2)
3
>>> @return_hook_for("demo1")
... def hook2(rv: int) -> int:
...     return rv - 1
>>> add(1, 2)
2
"""

__version__ = "0.1.0"
__author__ = "Koviubi56"
__email__ = "koviubi56@duck.com"
__license__ = "MIT"
__copyright__ = "Copyright (C) 2022 Koviubi56"
__description__ = "Hooks for functions."
__url__ = "https://github.com/koviubi56/hooksff"


import abc
import dataclasses
import functools
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Tuple,
    TypeVar,
    Union,
)

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


class HookResponse(abc.ABC):
    """An ABC for hook responses."""

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return a string representation of the hook response.

        Returns:
            str: A string representation of the hook response.
        """
        return f"<HookResponse {self.__class__.__qualname__}>"


class DoNothing(HookResponse):  # Default
    """A hook response to do nothing."""

    __slots__ = ()


class ReturnHookResponseWarning(UserWarning):
    """Probably this isn't what you want. Try `return_hook_for` instead."""


class HookTypeErrorWarning(UserWarning):
    """This is issued, when a TypeError was raised during a hook call."""


class UnknownHookResponseWarning(UserWarning):
    """This is issued, when a hook returns an unknown hook response."""


class Return(HookResponse):
    """
    A hook response to return a value.

    Note that if use this, the return hooks will NOT be called.
    """

    __slots__ = ("value",)

    def __init__(self, value: R, *, ignore_warning: bool = False):
        """
        Initialize a `Return` instance.

        Args:
            value (R): The value to return.
            ignore_warning (bool, optional): If True, no ReturnHookWarnings
            will be issued. Defaults to False.
        """
        if not ignore_warning:
            warnings.warn(
                "Probably this isn't what you want. Try `return_hook_for`"
                " instead.",
                ReturnHookResponseWarning,
                stacklevel=2,
            )
        self.value = value


class Change(HookResponse):
    """A hook response to change the arguments and/or keyword arguments."""

    __slots__ = ("args", "kwargs")

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize a `Change` instance.

        Args:
            *args: The positional arguments to change.
            **kwargs: The keyword arguments to change.
        """
        self.args = args
        self.kwargs = kwargs


hooks: Dict[str, List[Callable[P, HookResponse]]] = {}
return_hooks: Dict[str, List[Callable[[R], R]]] = {}


def remove_hooks_for(name: str, raise_on_keyerror: bool = False) -> None:
    """
    Remove all hooks for the given name.

    Args:
        name (str): The name of the hooks to remove.
        raise_on_keyerror (bool, optional): Whether to raise a KeyError if the
        name is not found. Defaults to False.

    Raises:
        KeyError: If no hooks, and no return hooks were found for the given
        name and `raise_on_keyerror` is truthy.
    """
    h = hooks.pop(name, None)
    r = return_hooks.pop(name, None)
    if (raise_on_keyerror) and (h is None) and (r is None):
        raise KeyError(name)


@dataclasses.dataclass(frozen=True, order=True)
class Args:
    """Positional and keyword arguments."""

    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]


def run_hooks_for(
    name: str,
    args: Any,
    kwargs: Any,
) -> Union[Args, Any]:
    """
    Run all hooks for the given name.

    Args:
        name (str): The name.
        args (Any): The positional arguments.
        kwargs (Any): The keyword arguments.

    Returns:
        Union[Args, Any]: The result of the hooks. If it's an Args, the
        function should be called with that args. If it's something else, it
        should be considered the return value of the function.
    """
    for hook in hooks.get(name, ()):
        try:
            hr = hook(*args, **kwargs)
        except TypeError as e:
            warnings.warn(
                f"{e.__class__.__name__}: {e}. Maybe you forgot to"
                " pass the right number of arguments?",
                HookTypeErrorWarning,
            )
            continue
        if (hr is None) or isinstance(hr, DoNothing):
            pass
        elif isinstance(hr, Return):
            return hr.value
        elif isinstance(hr, Change):
            args, kwargs = hr.args, hr.kwargs
        else:
            warnings.warn(
                f"Unknown HookResponse type {hr!r} ({type(hr)})",
                UnknownHookResponseWarning,
            )
    return Args(args, kwargs)


def run_return_hooks_for(name: str, got_rv: R) -> R:
    """
    Run all return hooks for the given name.

    Args:
        name (str): The name.
        got_rv (R): The return value.

    Returns:
        R: The return value.
    """
    rv = got_rv
    for hook in return_hooks.get(name, ()):
        rv = hook(rv)
    return rv


def mark_as_hookable(
    name: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Mark a function as hookable.

    Args:
        name (str): The name.

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]]: The decorator. If you call
        it you get the actual function.
    """

    def mah(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[R, Any]:
            arguments = run_hooks_for(name, args, kwargs)
            if not isinstance(arguments, Args):
                return arguments
            args, kwargs = arguments.args, arguments.kwargs
            rv = func(*args, **kwargs)
            return run_return_hooks_for(name, rv)

        return wrapper

    return mah


DUPE_MODE = Literal[
    "rem_nothing",
    "rem_name",
    "rem_qualname",
    "rem_mod_qualname",
    "rem_equals",
    "rem_is",
    "rem_code",
    "rem_any",
]
dupe_modes = DUPE_MODE.__args__


def _is_dupe(
    f1: Callable[..., Any], f2: Callable[..., Any], mode: DUPE_MODE
) -> bool:
    """
    Check if two functions are duplicates.

    Args:
        f1 (Callable[..., Any]): The first function.
        f2 (Callable[..., Any]): The second function.
        mode (DUPE_MODE): The mode to use.

    Returns:
        bool: Whether the two functions are duplicates.
    """
    if mode == "rem_nothing":
        return False
    if mode == "rem_name":
        return f1.__name__ == f2.__name__
    if mode == "rem_qualname":
        return f1.__qualname__ == f2.__qualname__
    if mode == "rem_mod_qualname":
        return (
            f"{f1.__module__}.{f1.__qualname__}"
            == f"{f2.__module__}.{f2.__qualname__}"
        )

    if mode == "rem_equals":
        return f1 == f2
    if mode == "rem_is":
        return f1 is f2
    if mode == "rem_code":
        return f1.__code__ == f2.__code__
    if mode == "rem_any":
        warnings.warn(
            "rem_any should not be passed to _is_dupe;"
            " it should be handled in is_dupe",
            RuntimeWarning,
        )
        return False


def is_dupe(
    f1: Callable[..., Any], f2: Callable[..., Any], mode: DUPE_MODE
) -> bool:
    """
    Check if two functions are duplicates.

    Args:
        f1 (Callable[..., Any]): The first function.
        f2 (Callable[..., Any]): The second function.
        mode (DUPE_MODE): The mode to use.

    Returns:
        bool: Whether the two functions are duplicates.
    """
    if mode == "rem_any":
        return any(
            _is_dupe(f1, f2, mode) for mode in dupe_modes if mode != "rem_any"
        )
    return _is_dupe(f1, f2, mode)


def already_exists(
    in_: Iterable[Callable[..., Any]],
    func: Callable[..., Any],
    mode: DUPE_MODE,
) -> bool:
    """
    Check if a function already exists in a list of functions.

    Args:
        in_ (Iterable[Callable[..., Any]]): The list of functions.
        func (Callable[..., Any]): The function to check for.
        mode (DUPE_MODE): The mode to use.

    Returns:
        bool: Whether the function already exists.
    """
    if mode == "rem_nothing":
        return False  # For faster performance
    return any(is_dupe(f, func, mode) for f in in_)


def hook_for(
    name: str,
    rem_dupe: DUPE_MODE = "rem_any",
) -> Callable[[Callable[P, HookResponse]], Callable[P, HookResponse]]:
    """
    Mark a function as a hook.

    Args:
        name (str): The name.
        rem_dupe (DUPE_MODE): The mode to use when removing duplicates.

    Returns:
        Callable[[Callable[P, HookResponse]], Callable[P, HookResponse]]: The
        decorator. If you call it you get the actual function.
    """

    def hf(func: Callable[P, HookResponse]) -> Callable[P, HookResponse]:
        hooks.setdefault(name, [])
        if not already_exists(hooks[name], func, rem_dupe):
            hooks[name].append(func)
        return func

    return hf


def return_hook_for(
    name: str,
    rem_dupe: DUPE_MODE = "rem_any",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Mark a function as a hook that changes the return value.

    Args:
        name (str): The name.
        rem_dupe (DUPE_MODE): The mode to use when removing duplicates.

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]]: The decorator. If you call
        it you get the actual function.
    """

    def rhf(func: Callable[P, R]) -> Callable[P, R]:
        return_hooks.setdefault(name, [])
        if not already_exists(return_hooks[name], func, rem_dupe):
            return_hooks[name].append(func)
        return func

    return rhf
