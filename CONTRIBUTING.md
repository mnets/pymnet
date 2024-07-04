# Developing `pymnet`

This package is a pure python package, where you can find the main modules in
the `pymnet/` directory and the documentation in the `docs/`. Most of the
method documentations are, however, directly pulled from method docstrings in
the code. The tests are located at `pymnet/tests/`.

## Getting started

The best way to begin contributing is by creating a fork of this project on GitHub,
making your modifications, and sending in a pull request. 
Refer to [GitHub
documentations][github-how-to] on the basic workflow.

Currently, the code is hosted on GitHub at https://github.com/mnets/pymnet.

Before commiting a lot of time and making big changes, it might be a good
idea to talk about it with the developers by creating an issue.

[github-how-to]: https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project

## Reporting bugs or suggesting improvments

Use [GitHub issues][github-issues] for reporting bugs or suggesting
improvments. It would help everyone involved if you could include a minimal
example to demonstrate the problem in isolation.

[github-issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue

## Installing from source

With the repository cloned in the current directory, you can use `pip` to 
install from the current directory:

```console
$ pip install --force-reinstall . 
```

The flag `--force-reinstall` ensures that a new install from the current
directory will happen even if you already have `pymnet` installed from another
source.

## Running tests

With the repository cloned in the current directory, you can run the
`pymnet.tests` module to run the tests:

```console
$ python -m pymnet.tests
```

## Building documentation

With the repository cloned in the current directory, you can build the
documentations using Sphinx. First, make sure all requirements for docs
are installed:

```console
$ python -m pip install -r doc/requirements.txt
```

You can build the docs using this command:

```console
$ sphinx-build doc/ doc/_build/html
```

You can start a local HTTP server using Python and click on the URL printed to
open the built documentations on your browser:
```console
$ python -m http.server -d doc/_build/html/
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

## Release

So far, we are not using GitHub releases. Releasing a new version is a three -step process: Bumping version number in `pyproject.toml`, building a wheel
file, and uploading it to PyPI.

You can build a new wheel using `pip`:

```console
$ pip wheel . --wheel-dir wheelhouse
```

This creates a wheel file for `pymnet` as well as all dependencies in the 
`wheelhouse/` directory. You can use [Twine][twine] to upload the pymnet wheel
to the Python Package Index:

```console
$ python -m twine upload wheelhouse/pymnet-$VERSION-py3-none-any.whl --verbose
```

Remember to replace `$VERSION` with the version in the generated file!

Uplading a new wheel under the `pymnet` project is only available to the
[package maintainers on PyPI][maintainers].

[twine]: https://twine.readthedocs.io/en/latest/
[maintainers]: https://pypi.org/project/pymnet/
