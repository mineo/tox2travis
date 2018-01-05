#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017, 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
import click
import logging


from .tox2travis import (generate_matrix_specification, get_all_environments,
                         fill_basepythons, travis_yml_header, travis_yml_footer,
                         ALL_VALID_FALLBACKS, BasePython, ALL_KNOWN_BASEPYTHONS)
from copy import deepcopy


@click.command()
@click.option("--custom-mapping", nargs=2, multiple=True)
@click.option("--fallback-python", type=click.Choice(ALL_VALID_FALLBACKS))
@click.option("--verbose", is_flag=True)
@click.argument("outfile", type=click.File("w"))
def main(custom_mapping, fallback_python, verbose, outfile):  # noqa: D103
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

    outfile.write(travis_yml_header())
    for matrix_entry in generate_matrix_specification(basepythons):
        outfile.write(matrix_entry)
    outfile.write(travis_yml_footer())


if __name__ == "__main__":
    main()
