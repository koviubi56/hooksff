# hooksff

[![Hits-of-Code](https://hitsofcode.com/github/koviubi56/hooksff?branch=main)](https://hitsofcode.com/github/koviubi56/hooksff/view?branch=main)
![Codacy grade](https://img.shields.io/codacy/grade/ac166a98fc554f4a919a6cf4aefe7b7c)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/koviubi56/hooksff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/koviubi56/hooksff/main.svg)](https://results.pre-commit.ci/latest/github/koviubi56/hooksff/main)
![CircleCI](https://img.shields.io/circleci/build/github/koviubi56/hooksff)
[![codecov](https://codecov.io/gh/koviubi56/hooksff/branch/main/graph/badge.svg?token=PdN47jJXR5)](https://codecov.io/gh/koviubi56/hooksff)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/koviubi56/hooksff/Linting)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![semantic-release](https://img.shields.io/badge/%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)
![GitHub](https://img.shields.io/github/license/koviubi56/hooksff)
![PyPI](https://img.shields.io/pypi/v/hooksff)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hooksff)
![PyPI - Format](https://img.shields.io/pypi/format/hooksff)

hooksff is a [Python library](https://docs.python.org/3/glossary.html#term-module) for making hooks.

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
