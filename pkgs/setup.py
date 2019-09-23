import os
from setuptools import setup

setup(
    name='biosails_biostacks_cli',
    version='0.1',
    packages=['biosails_biostacks_cli'],
    entry_points={
        'console_scripts': ['biostacks=biosails_biostacks_cli.cli:main'],
    })
