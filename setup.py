#!/usr/bin/env python

from pathlib import Path

from setuptools import find_packages, setup

__author__ = """Gabriel Richard Pereira"""
__email__ = "pereira.gabrielr@gmail.com"
__version__ = "0.1.0"

setup_path = Path(__file__).parent

with open(setup_path / "test_requirements.txt") as f:
    test_requirements = f.readlines()

with open(setup_path / "requirements.txt") as f:
    requirements = f.readlines()

setup(
    author=__author__,
    author_email=__email__,
    python_requires=">=3.7,<=3.9",
    description="DAGGR CLI",
    entry_points={
        "console_scripts": [
            "daggr=daggr.cli:daggr",
        ],
    },
    install_requires=requirements,
    include_package_data=True,
    package_data={'': ['*.yml']},
    keywords="daggr",
    name="daggr",
    packages=find_packages(include=["daggr", "daggr.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/gabriel-rp/daggr",
    version=__version__,
    zip_safe=False,
)
