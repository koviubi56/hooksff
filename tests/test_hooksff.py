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
import contextlib

import pytest

import hooksff


def setup_function():
    for name in ("**test", "**test2"):
        with contextlib.suppress(Exception):
            hooksff.remove_hooks_for(name)
        with contextlib.suppress(Exception):
            del hooksff.hooksff[name]
        with contextlib.suppress(Exception):
            del hooksff.return_hooks[name]


@hooksff.mark_as_hookable("**test")
def hookable(x, y, *, z):
    return x + y + z


def test_no_thing():
    assert hookable(1, 2, z=3) == 6


def test_none():
    @hooksff.hook_for("**test")
    def none(x, y, z):
        return None

    assert hookable(1, 2, z=3) == 6


def test_donothing():
    @hooksff.hook_for("**test")
    def donothing(x, y, z):
        return hooksff.DoNothing()

    assert hookable(1, 2, z=3) == 6


def test_return():
    @hooksff.hook_for("**test")
    def return_69(x, y, z):
        with pytest.warns(
            hooksff.ReturnHookWarning,
            match=r"Probably this isn't what you want\. Try `return_hook_for`"
            r" instead\.",
        ):
            return hooksff.Return("Hi")

    assert hookable(1, 2, z=3) == "Hi"


def test_change():
    @hooksff.hook_for("**test")
    def change_args(x, y, z):
        return hooksff.Change(3, 3, z=3)

    assert hookable(1, 2, z=3) == 9


def test_return_hooks_1():
    @hooksff.return_hook_for("**test")
    def return_hook(rv):
        return rv + 1

    assert hookable(1, 2, z=3) == 7


def test_return_hooks_2():
    @hooksff.return_hook_for("**test")
    def return_hook(rv):
        return rv

    assert hookable(1, 2, z=3) == 6


def test_return_hooks_3():
    @hooksff.return_hook_for("**test")
    def return_hook(rv):
        return rv - 3

    assert hookable(1, 2, z=3) == 3


def test_return_hooks_4():
    @hooksff.return_hook_for("**test")
    def return_hook(rv):
        # this is just for testing, DO NOT use something like this in
        # production; return hook's return value should match original
        # function's return value!
        pass

    assert hookable(1, 2, z=3) is None


def test_return_hooks_5():
    @hooksff.mark_as_hookable("**test2")
    def test2(txt: str):
        return "yes" if txt.strip() else "no"

    assert test2("  ") == "no"
    assert test2("quick fox") == "yes"

    @hooksff.return_hook_for("**test2")
    def return_hook(rv):
        return "Super! :)" if rv == "yes" else "Nope :("

    assert test2("  ") == "Nope :("
    assert test2("quick fox") == "Super! :)"
