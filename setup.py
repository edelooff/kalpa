#!/usr/bin/python

import os
from setuptools import (
    find_packages,
    setup)

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()


setup(
    name='kalpa',
    version='0.1',
    author='Elmer de Looff',
    author_email='elmer.delooff@gmail.com',
    description='Resource baseclasses for traversal in Pyramid ',
    long_description=README,
    url='http://variable-scope.com',
    keywords='pyramid traversal resource helper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'pytest']
)
