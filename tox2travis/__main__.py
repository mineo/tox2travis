#!/usr/bin/env python
# coding: utf-8
# Copyright © 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
import click


from .tox2travis import (generate_matrix_specification, get_all_environments,
                         fill_basepythons, travis_yml_header, travis_yml_footer,
                         ALL_KNOWN_BASEPYTHONS)


@click.command()
@click.option("--fallback-python", type=click.Choice(
    python.tox_version for python in ALL_KNOWN_BASEPYTHONS))
@click.argument("outfile", type=click.File("w"))
def main(fallback_python, outfile):  # noqa: D103
    envs = get_all_environments()
    basepythons = fill_basepythons(envs, fallback_python)

    outfile.write(travis_yml_header())
    for matrix_entry in generate_matrix_specification(basepythons):
        outfile.write(matrix_entry)
    outfile.write(travis_yml_footer())


if __name__ == "__main__":
    main()
