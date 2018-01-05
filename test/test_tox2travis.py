#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017, 2018 Wieland Hoffmann
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


_travis_yml_name = ".travis.yml"


def write_toxini(tmpdir, content):
    """
    :type directory: py.path.local
    :type content: str
    """
    file_ = tmpdir / "tox.ini"
    file_.write_text(content, "utf-8")
    return file_


def load_travis_yml(tmpdir):
    """
    :param str tmpdir:
    """
    filename = join(tmpdir, _travis_yml_name)
    with open(filename, "r") as fp:
        return yaml.load(fp)


def get_toxini_path_with_content(tmpdir, content):
    """
    :type tmpdir: py.path.local
    :type content: str
    """
    return fspath(write_toxini(tmpdir, content))


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
def test_simple_case(basepython):
    runner = CliRunner()

    with runner.isolated_filesystem():
        this_dir = Path(getcwd())
        get_toxini_path_with_content(this_dir, dedent("""\
        [tox]
        envlist = test
        [testenv:test]
        basepython={python}
        """.format(python=basepython.tox_version)))

        result = runner.invoke(main, [_travis_yml_name])
        assert result.exit_code == 0, result.output

        content = load_travis_yml(this_dir)
        includes = content["matrix"]["include"]
        expected = [{"env": "TOXENV=test", "python": basepython.travis_version}]
        assert expected == includes


@pytest.mark.parametrize("custom_target1", (tox2travis.TOX_CPYTHONS +
                                            tox2travis.TOX_JYTHONS +
                                            tox2travis.TOX_PYPYS +
                                            ["python_version_not_in_travis"]))
@pytest.mark.parametrize("custom_target2", (tox2travis.TOX_CPYTHONS +
                                            tox2travis.TOX_JYTHONS +
                                            tox2travis.TOX_PYPYS +
                                            ["python_version_not_in_travis"]))
def test_custom_mapping(custom_target1, custom_target2):
    runner = CliRunner()

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

        result = runner.invoke(main, [_travis_yml_name])
        assert result.exit_code == 0, result.output
        content = load_travis_yml(this_dir)
        includes = content["matrix"]["include"]
        assert includes is None, includes

        result = runner.invoke(main, ["--custom-mapping",
                                      "pythonsomething.something",
                                      custom_target1,
                                      "--custom-mapping",
                                      "pythonsomething.somethingelse",
                                      custom_target2,
                                      _travis_yml_name])

        assert result.exit_code == 0, result.output

        content = load_travis_yml(this_dir)
        includes = content["matrix"]["include"]
        assert includes is not None, content
        assert len(includes) == 2, includes

        expected = [{"env": "TOXENV=flake8", "python": custom_target1},
                    {"env": "TOXENV=test", "python": custom_target2}]

        assert expected == includes
