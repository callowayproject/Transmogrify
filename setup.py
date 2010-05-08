#!/usr/bin/env python

from setuptools import setup, find_packages
from subprocess import Popen, PIPE
import transmogrify, os

def read_file(the_file):
    current_dir = os.path.normpath(os.path.dirname(__file__))
    return open(os.path.join(current_dir, the_file)).read()

setup(
    name = 'transmogrify',
    version = transmogrify.get_version(),
    description = 'Allows for the dynamic alteration of images using the URL.',
    long_description = read_file('README'),
    author = 'Corey Oordt',
    author_email = 'coordt@washingtontimes.com',
    url = 'http://opensource.washingtontimes.com/projects/transmogrify/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
    ],
    install_requires=read_file('requirements.txt'),
    include_package_data = True,
    packages = find_packages(),
)
