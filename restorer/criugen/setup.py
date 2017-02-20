# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='criugen',
    version='0.1.0',
    description='Process restoration commands generator and tools',
    long_description=readme,
    author='Egor Gorbunov',
    author_email='egor-mailbox@ya.ru',
    url='https://github.com/egorbunov/v2criu/restorer/criugen',
    install_requires=[
        'crit'
    ],
    license=license_,
    packages=find_packages(exclude=('tests', 'docs'))
)
