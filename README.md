# tox2travis

![Run tox](https://github.com/mineo/tox2travis/workflows/Run%20tox/badge.svg)
[![Build Status](https://travis-ci.org/mineo/tox2travis.svg?branch=master)](https://travis-ci.org/mineo/tox2travis)

After installing, simply call `tox2travis` in a directory that
contains a `tox.ini` file. A `.travis.yml` file will be generated.

`tox2travis` will be able to map environment names using tox's
[default
environments](https://tox.readthedocs.io/en/latest/example/basic.html#a-simple-tox-ini-default-environments)
to the correct python version on Travis automatically.

## Non-standard environment names

If an environment name does not match one of the default environments
provided by tox, tox2travis will simply ignore it. To specify a python
version for such environments, use the `--fallback-python` command line
argument:

```
tox2travis --fallback-python pythonx.y
```

The value passed to the argument must be a valid
[basepython](https://tox.readthedocs.io/en/latest/config.html#conf-basepython).

## Custom basepython

If environments specified in `tox.ini` use a
[basepython](https://tox.readthedocs.io/en/latest/config.html#conf-basepython)
that can not be automatically mapped to one of the supported python
versions on Travis, use the `--custom-mapping` command line argument:

```
tox2travis --custom-mapping <basepython> <travis-python>
```

## GitHub Actions

Despite the name, `tox2travis` can also generate a configuration file
for [GitHub Actions](https://github.com/features/actions). Simply call
`tox2travis --output=actions` in a directory that contains a
`tox.ini` file. A new file `.github/workflows/tox.yml` will be
generated.
