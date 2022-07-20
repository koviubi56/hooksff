"""
HooksFF: hooksff for functions.

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
"""

import warnings
from typing import Callable
from unittest.mock import Mock

import pytest

import hooksff

HOOKABLE_NAME = "test"


def func1() -> None:
    """Useless function #1."""


def func2() -> None:
    """Useless function #2."""


@pytest.fixture(scope="function")
def hookable() -> Callable[[int, int], int]:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    @hooksff.mark_as_hookable(HOOKABLE_NAME)
    def _(x: int, y: int) -> int:
        return x - y

    @hooksff.hook_for(HOOKABLE_NAME)
    def _hook(x: int, y: int) -> int:
        return hooksff.Change(y, x)

    return _


def test_return_hook_response_warns() -> None:
    with pytest.warns(
        hooksff.ReturnHookResponseWarning,
        match=r"^Probably this isn't what you want\. Try `return_hook_for`"
        r" instead\.$",
    ):
        hooksff.Return(1)


def test_return_hook_response_doesnt_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        hooksff.Return(1, ignore_warning=True)


def test_remove_hooks_for(hookable: Callable[[int, int], int]) -> None:
    assert hookable(1, 2) == 1
    assert hooksff.hooks[HOOKABLE_NAME]

    hooksff.remove_hooks_for(HOOKABLE_NAME)

    assert hookable(1, 2) == -1
    with pytest.raises(KeyError, match=f"^{HOOKABLE_NAME!r}$"):
        hooksff.hooks[HOOKABLE_NAME]


def test_remove_hooks_for_no_hooks_no_raise(
    hookable: Callable[[int, int], int]
) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)
    hooksff.remove_hooks_for(HOOKABLE_NAME)
    # This should not raise an exception


def test_remove_hooks_for_no_hooks_raise(
    hookable: Callable[[int, int], int]
) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME, True)
    with pytest.raises(KeyError, match=f"^{HOOKABLE_NAME!r}$"):
        hooksff.remove_hooks_for(HOOKABLE_NAME, True)


def test_run_hooks_for_donothing(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    mock = Mock(return_value=hooksff.DoNothing())
    hooksff.hook_for(HOOKABLE_NAME)(mock)
    mock.assert_not_called()

    assert hooksff.run_hooks_for(HOOKABLE_NAME, (1, 2), {}) == hooksff.Args(
        (1, 2), {}
    )
    mock.assert_called_once_with(1, 2)


def test_run_hooks_for_none(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    mock = Mock(return_value=None)
    hooksff.hook_for(HOOKABLE_NAME)(mock)
    mock.assert_not_called()

    assert hooksff.run_hooks_for(HOOKABLE_NAME, (1, 2), {}) == hooksff.Args(
        (1, 2), {}
    )
    mock.assert_called_once_with(1, 2)


def test_run_hooks_for_return(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    @hooksff.hook_for(HOOKABLE_NAME)
    def _(x: int, y: int) -> int:
        return hooksff.Return(x + y, ignore_warning=True)

    assert hooksff.run_hooks_for(HOOKABLE_NAME, (1, 2), {}) == 3


def test_run_hooks_for_change(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    @hooksff.hook_for(HOOKABLE_NAME)
    def _(x: int, y: int) -> int:
        return hooksff.Change(y, 7)

    assert hooksff.run_hooks_for(HOOKABLE_NAME, (1, 2), {}) == hooksff.Args(
        (2, 7), {}
    )


def test_run_hooks_for_warns_unknown_response(
    hookable: Callable[[int, int], int]
) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    @hooksff.hook_for(HOOKABLE_NAME)
    def _(x: int, y: int) -> int:
        return "hello"

    with pytest.warns():
        assert hooksff.run_hooks_for(
            HOOKABLE_NAME, (1, 2), {}
        ) == hooksff.Args((1, 2), {})


def test_run_hooks_for(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    @hooksff.hook_for(HOOKABLE_NAME)
    def _() -> None:
        return None

    with pytest.warns(hooksff.HookTypeErrorWarning):
        assert hooksff.run_hooks_for(
            HOOKABLE_NAME, (1, 2), {}
        ) == hooksff.Args((1, 2), {})


def test_run_return_hooks_for(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)

    assert hooksff.run_return_hooks_for(HOOKABLE_NAME, 6) == 6

    @hooksff.return_hook_for(HOOKABLE_NAME)
    def _(rv: int) -> int:
        return -rv

    assert hooksff.run_return_hooks_for(HOOKABLE_NAME, 6) == -6


def test_mark_as_hookable() -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)
    assert hooksff.hooks.get(HOOKABLE_NAME) is None

    @hooksff.mark_as_hookable(HOOKABLE_NAME)
    def _() -> None:
        return None

    assert hooksff.hooks.get(HOOKABLE_NAME) is None
    assert _() is None


class Test_is_dupe:
    @staticmethod
    def test_rem_nothing() -> None:
        assert not hooksff._is_dupe(func1, func1, "rem_nothing")
        assert not hooksff._is_dupe(func1, func2, "rem_nothing")

    @staticmethod
    def test_rem_name() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_name")
        assert not hooksff._is_dupe(func1, func2, "rem_name")

    @staticmethod
    def test_rem_qualname() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_qualname")
        assert not hooksff._is_dupe(func1, func2, "rem_qualname")

    @staticmethod
    def test_rem_mod_qualname() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_mod_qualname")
        assert not hooksff._is_dupe(func1, func2, "rem_mod_qualname")

    @staticmethod
    def test_rem_equals() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_equals")
        assert not hooksff._is_dupe(func1, func2, "rem_equals")

    @staticmethod
    def test_rem_is() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_is")
        assert not hooksff._is_dupe(func1, func2, "rem_is")

    @staticmethod
    def test_rem_code() -> None:
        assert hooksff._is_dupe(func1, func1, "rem_code")
        assert not hooksff._is_dupe(func1, func2, "rem_code")

    @staticmethod
    def test_rem_any() -> None:
        with pytest.warns(
            RuntimeWarning,
            match=r"rem_any should not be passed to _is_dupe; it should be"
            r" handled in is_dupe",
        ):
            hooksff._is_dupe(func1, func1, "rem_any")
        with pytest.warns(
            RuntimeWarning,
            match=r"rem_any should not be passed to _is_dupe; it should be"
            r" handled in is_dupe",
        ):
            hooksff._is_dupe(func1, func2, "rem_any")


class Testis_dupe:
    @staticmethod
    def test_rem_nothing() -> None:
        assert not hooksff.is_dupe(func1, func1, "rem_nothing")
        assert not hooksff.is_dupe(func1, func2, "rem_nothing")

    @staticmethod
    def test_rem_name() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_name")
        assert not hooksff.is_dupe(func1, func2, "rem_name")

    @staticmethod
    def test_rem_qualname() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_qualname")
        assert not hooksff.is_dupe(func1, func2, "rem_qualname")

    @staticmethod
    def test_rem_mod_qualname() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_mod_qualname")
        assert not hooksff.is_dupe(func1, func2, "rem_mod_qualname")

    @staticmethod
    def test_rem_equals() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_equals")
        assert not hooksff.is_dupe(func1, func2, "rem_equals")

    @staticmethod
    def test_rem_is() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_is")
        assert not hooksff.is_dupe(func1, func2, "rem_is")

    @staticmethod
    def test_rem_code() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_code")
        assert not hooksff.is_dupe(func1, func2, "rem_code")

    @staticmethod
    def test_rem_any() -> None:
        assert hooksff.is_dupe(func1, func1, "rem_any")
        assert not hooksff.is_dupe(func1, func2, "rem_any")


class Testalready_exists:
    @staticmethod
    def test_rem_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
        mock = Mock()
        with monkeypatch.context() as mp:
            mp.setattr("builtins.any", mock)
            assert not hooksff.already_exists([func1], func1, "rem_nothing")
            assert not hooksff.already_exists([func1], func2, "rem_nothing")
        mock.assert_not_called()

    @staticmethod
    def test_rem_name() -> None:
        assert hooksff.already_exists([func1], func1, "rem_name")
        assert not hooksff.already_exists([func1], func2, "rem_name")

    @staticmethod
    def test_rem_qualname() -> None:
        assert hooksff.already_exists([func1], func1, "rem_qualname")
        assert not hooksff.already_exists([func1], func2, "rem_qualname")

    @staticmethod
    def test_rem_mod_qualname() -> None:
        assert hooksff.already_exists([func1], func1, "rem_mod_qualname")
        assert not hooksff.already_exists([func1], func2, "rem_mod_qualname")

    @staticmethod
    def test_rem_equals() -> None:
        assert hooksff.already_exists([func1], func1, "rem_equals")
        assert not hooksff.already_exists([func1], func2, "rem_equals")

    @staticmethod
    def test_rem_is() -> None:
        assert hooksff.already_exists([func1], func1, "rem_is")
        assert not hooksff.already_exists([func1], func2, "rem_is")

    @staticmethod
    def test_rem_code() -> None:
        assert hooksff.already_exists([func1], func1, "rem_code")
        assert not hooksff.already_exists([func1], func2, "rem_code")

    @staticmethod
    def test_rem_any() -> None:
        assert hooksff.already_exists([func1], func1, "rem_any")
        assert not hooksff.already_exists([func1], func2, "rem_any")


def test_hook_for(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)
    mock = Mock()
    hooksff.hook_for(HOOKABLE_NAME)(mock)
    mock.assert_not_called()
    assert hooksff.hooks[HOOKABLE_NAME] == [mock]
    assert hooksff.return_hooks.get(HOOKABLE_NAME) is None


def test_return_hook_for(hookable: Callable[[int, int], int]) -> None:
    hooksff.remove_hooks_for(HOOKABLE_NAME)
    mock = Mock()
    hooksff.return_hook_for(HOOKABLE_NAME)(mock)
    mock.assert_not_called()
    assert hooksff.hooks.get(HOOKABLE_NAME) is None
    assert hooksff.return_hooks[HOOKABLE_NAME] == [mock]
