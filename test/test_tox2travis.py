#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017, 2018, 2019 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest
import yaml


from click.testing import CliRunner
from os import fspath, getcwd
from os.path import join
from pathlib import Path
from textwrap import dedent
from tox2travis import tox2travis
from tox2travis.__main__ import main


def write_file(tmpdir, filename, content):
    """
    :type directory: py.path.local
    :type content: str
    """
    file_ = tmpdir / filename
    file_.write_text(content, "utf-8")
    return file_


def read_travis_yml(tmpdir):
    """
    :param str tmpdir:
    """
    filename = join(tmpdir, tox2travis.TRAVIS_YAML)
    with open(filename, "r") as fp:
        return fp.read()


def load_travis_yml(tmpdir):
    """
    :param str tmpdir:
    """
    return yaml.load(read_travis_yml(tmpdir))


def get_toxini_path_with_content(tmpdir, content):
    """
    :type tmpdir: py.path.local
    :type content: str
    """
    return fspath(write_file(tmpdir, "tox.ini", content))


def test_get_all_environments_sorts(tmpdir):
    toxini = get_toxini_path_with_content(tmpdir, dedent("""\
    [tox]
    envlist = py36,py27
    """))
    configs = tox2travis.get_all_environments(toxini)
    expected_basepythons = ["python2.7", "python3.6"]
    actual_basepythons = [env.basepython for env in configs]
    assert actual_basepythons == expected_basepythons


def test_unkown_fallback_raises(basepythons):
    invalid_fallback_name = "this_is_not_a_valid_python"
    with pytest.raises(ValueError, match=f"{invalid_fallback_name} .*"):
        tox2travis.fill_basepythons(basepythons,
                                    [],
                                    fallback_basepython=invalid_fallback_name)


@pytest.mark.parametrize("fallback", tox2travis.ALL_VALID_FALLBACKS)
def test_fallback_is_used(basepythons, tmpdir, fallback):
    toxini = get_toxini_path_with_content(tmpdir, dedent("""\
    [tox]
    envlist = flake8
    """))
    configs = tox2travis.get_all_environments(toxini)
    basepythons = tox2travis.fill_basepythons(basepythons,
                                              configs,
                                              fallback)
    for bp in basepythons:
        if bp.tox_version == fallback:
            assert bp.environments[0].envname == "flake8"
            break
    else:
        pytest.fail("Did not find the fallback BasePython")

    for bp in basepythons:
        if bp.tox_version == fallback:
            continue
        assert len(bp.environments) == 0


@pytest.mark.parametrize("basepython", tox2travis.ALL_KNOWN_BASEPYTHONS)
def test_simple_case(basepython, snapshot):
    runner = CliRunner()
    actual = None

    with runner.isolated_filesystem():
        this_dir = Path(getcwd())
        get_toxini_path_with_content(this_dir, dedent("""\
        [tox]
        envlist = test
        [testenv:test]
        basepython={python}
        """.format(python=basepython.tox_version)))

        result = runner.invoke(main)
        assert result.exit_code == 0, result.output

        actual = read_travis_yml(this_dir)

    snapshot.snapshot_dir = f"snapshots/travis_simple"
    snapshot.assert_match(actual, f"{basepython.tox_version}")

@pytest.mark.parametrize("custom_target1", (tox2travis.ALL_KNOWN_BASEPYTHONS))
@pytest.mark.parametrize("custom_target2", (tox2travis.ALL_KNOWN_BASEPYTHONS))
def test_custom_mapping(custom_target1, custom_target2, snapshot):
    runner = CliRunner()
    actual = None

    with runner.isolated_filesystem():
        this_dir = Path(getcwd())
        get_toxini_path_with_content(this_dir, dedent("""\
        [tox]
        envlist = flake8,test
        [testenv:flake8]
        basepython=pythonsomething.something
        [testenv:test]
        basepython=pythonsomething.somethingelse
        """))

        result = runner.invoke(main)
        assert result.exit_code == 0, result.output
        content = load_travis_yml(this_dir)
        includes = content["matrix"]["include"]
        assert includes is None, includes

        result = runner.invoke(main, ["--custom-mapping",
                                      "pythonsomething.something",
                                      custom_target1.travis_version,
                                      "--custom-mapping",
                                      "pythonsomething.somethingelse",
                                      custom_target2.travis_version])

        assert result.exit_code == 0, result.output
        actual = read_travis_yml(this_dir)

    snapshot.snapshot_dir = f"snapshots/travis_two_custom"
    snapshot.assert_match(actual, f"{custom_target1.travis_version}_{custom_target2.travis_version}.yml")
