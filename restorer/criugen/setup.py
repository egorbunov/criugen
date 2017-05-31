# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='criugen',
    version='0.1.0',
    description='Another approach for process tree restoration',
    long_description=readme,
    author='Egor Gorbunov',
    author_email='egor-mailbox@ya.ru',
    url='https://github.com/egorbunov/v2criu/restorer/criugen',
    install_requires=[
        'crit',  # there is no such pip module, but can be installed from CRIU sources
        'argparse'
    ],
    license=license_,
    packages=find_packages(exclude=('tests', 'docs'))
)
