#!/usr/bin/env python

import json
from setuptools import setup, find_packages

from aiida_dummy import __version__


if __name__ == '__main__':

    with open('setup.json', 'r') as info:
        kwargs = json.load(info)

    setup(packages=find_packages(), version=__version__, **kwargs)
