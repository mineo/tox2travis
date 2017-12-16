#!/usr/bin/env python3
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
from textwrap import dedent, indent
from tox.config import parseconfig


class UnkownBasePython(Exception):
    """Exception raised when an unkown base python was found."""

    def __init__(self, basepython):  # noqa: D400
        """:param str basepython:"""
        self.basepython = basepython


class BasePython:
    """A base python version in tox and travis and its environments."""

    def __init__(self, tox_version, travis_version, environments=None):  # noqa: D400,E501
        """
        :param str tox_version:
        :param str travis_version:
        :param [tox.config.TestenvConfig] environments:
        """
        self.tox_version = tox_version
        self.travis_version = travis_version
        self._environments = environments or []

    def add_environment(self, environment):
        """Add a new environment to this python version.
        :param self:
        :param environment:
        """
        if environment not in self._environments:
            self._environments.append(environment)

    @property
    def environments(self):
        """Return a list of all environments that use this python version.

        :rtype: [tox.config.TestenvConfig]
        """
        return self._environments


# https://tox.readthedocs.io/en/latest/example/basic.html#a-simple-tox-ini-default-environments
# Available “default” test environments names are:
#
#   py
#   py2
#   py27
#   py3
#   py34
#   py35
#   py36
#   py37
#   jython
#   pypy
#   pypy3
#: All CPython versions known to tox
TOX_CPYTHONS = ["2.7", "3.4", "3.5", "3.6"]
#: All Jython versions known to tox
TOX_JYTHONS  = ["jython"]  # noqa: E221
#: All pypy versions known to tox
TOX_PYPYS    = ["pypy", "pypy3"]  # noqa: E221
#: All Python development versions supported by tox and travis
TOX_DEVPTHONS = [BasePython("python3.7", "3.7-dev")]

ALL_KNOWN_BASEPYTHONS = [
    BasePython("python{version}".format(version=version), version)
    for version in TOX_CPYTHONS
]

ALL_KNOWN_BASEPYTHONS.extend(BasePython(version, version)
                             for version in TOX_JYTHONS)
ALL_KNOWN_BASEPYTHONS.extend(BasePython(version, version)
                             for version in TOX_PYPYS)
ALL_KNOWN_BASEPYTHONS.extend(TOX_DEVPTHONS)


def get_all_environments():
    """Get a list of all tox environments.

    :rtype: [tox.config.TestenvConfig]
    """
    config = parseconfig([])
    envconfigs = sorted(config.envconfigs.values(), key=lambda e: e.envname)
    return envconfigs


def fill_basepythons(envconfigs, fallback_basepython=None):  # noqa: D400
    """Return a list of :type:`BasePython` objects with their environments
    populated from `envconfigs.

    :rtype: [BasePython]
    """
    basepythons = {basepython.tox_version: basepython
                   for basepython in ALL_KNOWN_BASEPYTHONS}
    all_basepythons = basepythons.keys()

    if (fallback_basepython is not None and
        fallback_basepython not in all_basepythons):
        raise ValueError("{} is not a known basepython, but was specified as the fallback".format(fallback_basepython))  # noqa: E501

    for envconfig in envconfigs:
        basepython = envconfig.basepython
        if basepython in all_basepythons:
            basepythons[basepython].add_environment(envconfig)
        else:
            if fallback_basepython is not None:
                basepythons[fallback_basepython].add_environment(envconfig)

    return basepythons.values()


def travis_yml_header():
    """Return the .travis.yml header."""
    return dedent("""\
    language: python
    cache: pip
    matrix:
      include:
    """)


def travis_yml_footer():
    """Return the .travis.yml footer."""
    return dedent("""\
    install:
      - travis_retry pip install tox
    script:
      - travis_retry tox
    """)


def generate_matrix_specification(basepythons):
    """Generate the matrix entries for all `basepythons`.

    :type basepythons: [BasePython]
    :rtype: [str]
    """
    for basepython in basepythons:
        for entry in generate_specs_for_basepython(basepython):
            indented = indent(entry, '  ')
            yield indented


def generate_specs_for_basepython(basepython):
    """Return the matrix entries for `basepython`.

    :type basepython: BasePython
    :rtype: str
    """
    single_entry_spec = dedent("""\
    - python: {python}
      env: TOXENV={toxenv}
    """)
    travis_version = basepython.travis_version
    for environment in basepython.environments:
        yield single_entry_spec.format(python=travis_version,
                                       toxenv=environment.envname)
