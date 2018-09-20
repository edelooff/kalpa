import os
from setuptools import setup, find_packages


def contents(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename)) as fp:
        return fp.read()


setup(
    name='kalpa',
    version='0.5.0',
    packages=find_packages(),
    author='Elmer de Looff',
    author_email='elmer.delooff@gmail.com',
    description='Resource baseclasses for traversal in Pyramid ',
    long_description=contents('README.rst'),
    keywords='pyramid traversal resource helper',
    license='BSD',
    url='https://github.com/edelooff/kalpa',
    install_requires=['six'],
    extras_require={
        'test': ['pyramid', 'pytest-runner', 'pytest']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'])
