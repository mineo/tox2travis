#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017, 2018, 2020 Wieland Hoffmann
# License: MIT, see LICENSE for details
import click
import logging


from .tox2travis import (get_all_environments,
                         fill_basepythons,
                         ALL_VALID_FALLBACKS, BasePython, ALL_KNOWN_BASEPYTHONS,
                         ALL_WRITERS)
from copy import deepcopy


@click.command()
@click.option("--custom-mapping", nargs=2, multiple=True)
@click.option("--fallback-python", type=click.Choice(ALL_VALID_FALLBACKS))
@click.option("--output",
              default=ALL_WRITERS[0].name,
              type=click.Choice([w.name for w in ALL_WRITERS]))
@click.option("--verbose", is_flag=True)
# @click.option("outfile", type=click.File("w"), default=TRAVIS_YAML)
def main(custom_mapping, fallback_python, output, verbose):  # noqa: D103
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    envs = get_all_environments()

    basepythons = deepcopy(ALL_KNOWN_BASEPYTHONS)
    for mapping in custom_mapping:
        basepython, travis_version = mapping
        basepythons.append(BasePython(basepython, travis_version))

    basepythons = fill_basepythons(basepythons, envs, fallback_python)

    writer = None
    for w in ALL_WRITERS:
        if w.name == output:
            writer = w
            break

    with w() as writer:
        writer.header()
        writer.generate_matrix_specifications(basepythons)
        writer.footer()


if __name__ == "__main__":
    main()
