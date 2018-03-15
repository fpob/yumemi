from setuptools import setup, find_packages
from pip.req import parse_requirements
from os import path

import yumemi


setup(
    name='yumemi',
    version=yumemi.__version__,
    description='AniDB library and simple CLI client.',
    author='Filip Pobořil',
    author_email='tsuki@fpob.eu',
    license='BSD',
    packages=['yumemi'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'yumemi=yumemi.cli:main'
        ],
    },
)
