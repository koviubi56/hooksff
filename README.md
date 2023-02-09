# hooksff

# DEPRECATED

There are probably a lot of tools out there that do hooks, and are way better than this.
Feel free to fork this repo if you _really_ want to use it.

<strike>hooksff is a [Python library](https://docs.python.org/3/glossary.html#term-module) for making hooks.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install hooksff. _[Need more help?](https://packaging.python.org/en/latest/tutorials/installing-packages/)_

```bash
pip install hooksff
```

## Requirements

hooksff requires Python 3.7 or higher.
The required packages can be found in the [requirements.txt](requirements.txt) file.

_[Click here to see these requirements in the `setup.cfg` file](setup.cfg#L27-L29)_

## Usage

For more information, see the [wiki](https://github.com/koviubi56/hooksff/wiki).

### Return hooks

```python
>>> import hooksff
>>> @hooksff.mark_as_hookable("my_hook")
... def my_func(x, y):
...     return x + y
>>> my_func(1, 2)
3
>>> @hooksff.return_hook_for("my_hook")
... def my_hook(rv):
...     return rv * 2
>>> my_func(1, 2)
6
```

### "DoNothing" hooks

```python
>>> import hooksff
>>> @hooksff.mark_as_hookable("my_hook")
... def my_func(x, y):
...     return x + y
>>> my_func(1, 2)
3
>>> @hooksff.hook_for("my_hook")
... def nothing(x, y):
...     return
...     # or `return hooksff.DoNothing()`
>>> my_func(1, 2)
3
```

### "Return" hooks

```python
>>> import hooksff
>>> @hooksff.mark_as_hookable("my_hook")
... def my_func(x, y):
...     return x + y
>>> my_func(1, 2)
3
>>> @hooksff.hook_for("my_hook")
... def return_hook(x, y):
...     return hooksff.Return(x - y)
>>> my_func(1, 2)
-1
```

### "Change" hooks

```python
>>> import hooksff
>>> @hooksff.mark_as_hookable("my_hook")
... def my_func(x, y):
...     return x + y
>>> my_func(1, 2)
3
>>> @hooksff.hook_for("my_hook")
... def change_hook(x, y):
...     return hooksff.Change(x, 6)
>>> my_func(1, 2)
7
```

## Support

Questions should be asked in the [Discussions tab](https://github.com/koviubi56/hooksff/discussions/categories/q-a).

Feature requests and bug reports should be reported in the [Issues tab](https://github.com/koviubi56/hooksff/issues/new/choose).

Security vulnerabilities should be reported as described in our [Security policy](https://github.com/koviubi56/hooksff/security/policy) _(the [SECURITY.md](SECURITY.md) file)_.

## Contributing

[Pull requests](https://github.com/koviubi56/hooksff/blob/main/CONTRIBUTING.md#pull-requests) are welcome. For major changes, please [open an issue first](https://github.com/koviubi56/hooksff/issues/new/choose) to discuss what you would like to change.

Please make sure to update [tests](https://docs.pytest.org/en/stable/getting-started.html) as appropriate, and add entries to [the changelog](CHANGELOG.md).

For more information, please read the [contributing guidelines](CONTRIBUTING.md).

## Authors and acknowledgments

A list of nice people who helped this project can be found in the [CONTRIBUTORS](CONTRIBUTORS) file.

## License

[MIT](LICENSE)
</strike>
