#!/usr/bin/env python
# encoding: utf-8

import os, sys
from setuptools import setup

setup(
    # metadata
    name='pfp',
    description='An 010 template interpreter for Python',
    long_description="""
        pfp is an 010 template interpreter for Python. It accepts an
        input data stream and an 010 template and returns a modifiable
        DOM of the parsed data. Extensions have also been added to the
        010 template syntax to allow for linked fields (e.g. checksums,
        length calculations, etc), sub structures in compressed data,
        etc.
    """,
    license='MIT',
    version='0.1.15',
    author='James Johnson',
    maintainer='James Johnson',
    author_email='d0c.s4vage@gmail.com',
    url='https://github.com/d0c-s4vage/pfp',
    platforms='Cross Platform',
    download_url="https://github.com/d0c-s4vage/pfp/tarball/v0.1.15",
    install_requires = open(os.path.join(os.path.dirname(__file__), "requirements.txt")).read().split("\n"),
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',],
    packages=['pfp', 'pfp.native'],
)
