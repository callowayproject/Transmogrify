#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages


version = __import__('transmogrify').get_version()

if sys.argv[-1] == 'publish':
    os.system('python setup.py bdist_wheel upload')
    print("You probably want to also tag the version now:")
    print("  python setup.py tag")
    sys.exit()
elif sys.argv[-1] == 'tag':
    cmd = "git tag -a %s -m 'version %s';git push --tags" % (version, version)
    os.system(cmd)
    sys.exit()


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


def get_readme():
    """Return the README file contents. Supports text,rst, and markdown"""
    for name in ('README', 'README.rst', 'README.md'):
        if os.path.exists(name):
            return read_file(name)
    return ''

# Use the docstring of the __init__ file to be the description
DESC = " ".join(__import__('transmogrify').__doc__.splitlines()).strip()

setup(
    name='transmogrify',
    version=version.replace(' ', '-'),
    description=DESC,
    long_description=get_readme(),
    author='Corey Oordt',
    author_email='coreyoordt@gmail.com',
    url='http://github.com/callowayproject/Transmogrify/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
    ],
    install_requires=read_file('requirements.txt'),
    include_package_data=True,
    packages=find_packages(exclude=['example*', ]),
    scripts=['bin/configure_transmogrify'],
    zip_safe=False
)
