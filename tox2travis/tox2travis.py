#!/usr/bin/env python3
# coding: utf-8
# Copyright © 2017, 2018, 2019, 2020 Wieland Hoffmann
# License: MIT, see LICENSE for details
import logging


from contextlib import ExitStack
from os import makedirs
from os.path import dirname
from textwrap import dedent, indent
from tox.config import parseconfig


class UnkownBasePython(Exception):
    """Exception raised when an unkown base python was found."""

    def __init__(self, basepython):  # noqa: D400
        """:param str basepython:"""
        self.basepython = basepython


class BasePython:
    """A base python version in tox and travis and its environments."""

    def __init__(self, tox_version, travis_version, environments=None, actions_version=None):  # noqa: D400,E501
        """
        :param str tox_version:
        :param str travis_version:
        :param [tox.config.TestenvConfig] environments:
        :param str actions_version:
        """
        self.tox_version = tox_version
        self.travis_version = travis_version
        self._environments = environments or []
        self.actions_version = actions_version or travis_version

    def add_environment(self, environment):
        """Add a new environment to this python version.

        :param self:
        :param environment:
        """
        if environment not in self._environments:
            self._environments.append(environment)

    def _clear_environments(self):
        """Clear the list of environments associated with this python version.

        :param self:
        """
        self._environments.clear()

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
#   py38
#   jython
#   pypy
#   pypy2
#   pypy27
#   pypy3
#   pypy35
#   py26, py32 and py33 also still work
#
# This list could also be generated from tox.config.default_factors, but not
# all of them map directly to a version of python supported by travis (for
# example py37/python3.7 should map to "3.7-dev" at the time of this writing).

#: All CPython versions known to tox
TOX_CPYTHONS = ["2.7", "3.5", "3.6", "3.7", "3.8"]
#: All pypy versions known to tox and travis
# https://docs.travis-ci.com/user/reference/xenial/#python-support
TOX_PYPYS    = [BasePython("pypy", "pypy2.7-6.0"), BasePython("pypy2", "pypy2.7-6.0", actions_version="pypy2"), BasePython("pypy3", "pypy3.5-6.0", actions_version="pypy3")]  # noqa: E221,E501
#: All Python development versions supported by tox and travis
TOX_DEVPTHONS = []

ALL_KNOWN_BASEPYTHONS = [
    BasePython("python{version}".format(version=version), version)
    for version in TOX_CPYTHONS
]

ALL_KNOWN_BASEPYTHONS.extend(TOX_PYPYS)
ALL_KNOWN_BASEPYTHONS.extend(TOX_DEVPTHONS)

#: All strings that can be used as a fallback
ALL_VALID_FALLBACKS = [python.tox_version for python in ALL_KNOWN_BASEPYTHONS]


def get_all_environments(toxini=None):
    """Get a list of all tox environments.

    :type toxini: str
    :rtype: [tox.config.TestenvConfig]
    """
    if toxini is None:
        config = parseconfig([])
    else:
        config = parseconfig(["-c", toxini])
    envconfigs = sorted(config.envconfigs.values(), key=lambda e: e.envname)
    return envconfigs


def fill_basepythons(basepythons, envconfigs, fallback_basepython=None):  # noqa: D400, E501
    """Return a list of :type:`BasePython` objects with their environments
    populated from `envconfigs.

    :type basepythons: [BasePython]
    :type envconfigs: [tox.config.TestenvConfig]
    :type fallback_basepython: str
    :rtype: [BasePython]
    """
    basepythons = {basepython.tox_version: basepython
                   for basepython in basepythons}
    all_basepythons = basepythons.keys()

    if (fallback_basepython is not None and
        fallback_basepython not in all_basepythons):
        raise ValueError("{} is not a known basepython, but was specified as the fallback".format(fallback_basepython))  # noqa: E501

    for envconfig in envconfigs:
        basepython = envconfig.basepython
        if basepython in all_basepythons:
            bp = basepythons[basepython]
            logging.debug("%s uses %s (%s)", envconfig.envname, basepython,
                          bp.travis_version)
            bp.add_environment(envconfig)
        else:
            if fallback_basepython is not None:
                bp = basepythons[fallback_basepython]
                logging.debug("%s uses %s (fallback: %s)", envconfig.envname,
                              basepython, bp.travis_version)
                bp.add_environment(envconfig)
    return list(basepythons.values())


class WriterBase(ExitStack):
    """Base class for all writers, allowing use as a context manager."""

    def __init__(self):
        super().__init__()
        self.outfile = None

    def __enter__(self):
        super().__enter__()
        dir_ = dirname(self.filename)
        if dir_:
            makedirs(dir_, exist_ok=True)
        self.outfile = self.enter_context(open(self.filename, "w"))
        return self


class ActionsWriter(WriterBase):
    """A class for writing a GitHub actions yaml file."""

    filename = ".github/workflows/tox.yml"
    name = "actions"

    def header(self):
        """Write the tox.yml header."""
        text = dedent("""\
        name: Python package
        on: [pull_request, push]
        jobs:
          build:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                include:
        """)
        self.outfile.write(text)

    def footer(self):
        """Write the tox.yml footer."""
        text = dedent("""\
            steps:
            - uses: actions/checkout@v2
            - name: Set up Python ${{ matrix.python-version }}
              uses: actions/setup-python@v2
              with:
                python-version: ${{ matrix.python-version }}
            - uses: actions/cache@v1
              with:
                path: ~/.cache/pip
                key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
                restore-keys: |
                  ${{ runner.os }}-pip-
            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install tox
            - name: Test with tox
              run: |
                tox -e ${{ matrix.env }}
        """)  # noqa: E501
        indented = indent(text, ' ' * 4)
        self.outfile.write(indented)

    def generate_matrix_specifications(self, basepythons):
        """Write the matrix entries for all `basepythons`.

        :type basepythons: [BasePython]
        :rtype: [str]
        """
        for basepython in basepythons:
            for entry in self.generate_specs_for_basepython(basepython):
                indented = indent(entry, ' ' * 10)
                self.outfile.write(indented)

    def generate_specs_for_basepython(self, basepython):
        """Write the matrix entries for `basepython`.

        :type basepython: BasePython
        :rtype: [str]
        """
        single_entry_spec = dedent("""\
        - python-version: "{python}"
          env: {toxenv}
        """)
        actions_version = basepython.actions_version
        for environment in basepython.environments:
            yield single_entry_spec.format(python=actions_version,
                                           toxenv=environment.envname)


class TravisWriter(WriterBase):
    """A class for writing a .travis.yml file."""

    filename = ".travis.yml"
    name = "travis"

    def header(self):
        """Write the .travis.yml header."""
        text = dedent("""\
        language: python
        cache: pip
        dist: xenial
        matrix:
          include:
        """)
        self.outfile.write(text)

    def footer(self):
        """Write the .travis.yml footer."""
        text = dedent("""\
        install:
          - travis_retry pip install tox
        script:
          - travis_retry tox
        """)
        self.outfile.write(text)

    def generate_matrix_specifications(self, basepythons):
        """Write the matrix entries for all `basepythons`.

        :type basepythons: [BasePython]
        :rtype: [str]
        """
        for basepython in basepythons:
            for entry in self.generate_specs_for_basepython(basepython):
                indented = indent(entry, '  ')
                self.outfile.write(indented)

    def generate_specs_for_basepython(self, basepython):
        """Write the matrix entries for `basepython`.

        :type basepython: BasePython
        :rtype: [str]
        """
        single_entry_spec = dedent("""\
        - python: "{python}"
          env: TOXENV={toxenv}
        """)
        travis_version = basepython.travis_version
        for environment in basepython.environments:
            yield single_entry_spec.format(python=travis_version,
                                           toxenv=environment.envname)


ALL_WRITERS = [TravisWriter, ActionsWriter]
