#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest


from os import fspath
from textwrap import dedent
from tox2travis import tox2travis


def write_toxini(tmpdir, content):
    """
    :type directory: py.path.local
    :type content: str
    """
    file_ = tmpdir / "tox.ini"
    file_.write_text(content, "utf-8")
    return file_


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
