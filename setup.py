#!/usr/bin/env python3
from __future__ import print_function
from codecs import open
from setuptools import setup


setup(name="tox2travis",
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      packages=["tox2travis"],
      package_dir={"tox2travis": "tox2travis"},
      download_url="https://github.com/mineo/tox2travis/tarball/master",
      url="http://github.com/mineo/tox2travis",
      license="MIT",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.6"],
      description="Automatically generate .travis.yml from tox.ini",
      long_description=open("README.md", encoding="utf-8").read(),
      long_description_content_type='text/markdown',
      install_requires=["click", "tox"],
      python_requires='>=3.6',
      entry_points='''
      [console_scripts]
      tox2travis=tox2travis.__main__:main
      ''',
      setup_requires=["setuptools_scm", "pytest-runner"],
      use_scm_version={"write_to": "tox2travis/version.py"},
      extras_require={
          'docs': ['sphinx']
      },
      tests_require=["pytest", "pytest-snapshot", "pyyaml"]
      )
