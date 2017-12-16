#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest


from tox2travis import tox2travis


@pytest.fixture(autouse=True)
def reset_basepythons():
    """Clears the list of known environments from all python versions."""
    for bp in tox2travis.ALL_KNOWN_BASEPYTHONS:
        bp._clear_environments()
