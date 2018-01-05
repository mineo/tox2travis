#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017, 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest


from copy import deepcopy
from tox2travis import tox2travis


@pytest.fixture()
def basepythons():
    """

    """
    return deepcopy(tox2travis.ALL_KNOWN_BASEPYTHONS)
