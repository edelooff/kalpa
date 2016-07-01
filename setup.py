#!/usr/bin/python

import os
from setuptools import (
    find_packages,
    setup)


def contents(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename)) as fp:
        return fp.read()


setup(
    name='kalpa',
    version='0.2',
    author='Elmer de Looff',
    author_email='elmer.delooff@gmail.com',
    description='Resource baseclasses for traversal in Pyramid ',
    long_description=contents('README.rst'),
    url='http://variable-scope.com',
    keywords='pyramid traversal resource helper',
    classifiers=[
        'Development Status :: 2 - Alpha',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'test': ['pyramid', 'pytest-runner', 'pytest']
    },
)
