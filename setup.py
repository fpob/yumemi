from setuptools import setup, find_packages
from pip.req import parse_requirements
from os import path

import yumemi


setup(
    name='yumemi',
    version=yumemi.__version__,
    description='AniDB client',
    author='Filip Pobořil',
    author_email='tsuki@fpob.eu',
    license='BSD',
    packages=['yumemi'],
    install_requires=['click'],
    extras_require={
        'xattr': ['xattr'],
    },
    entry_points={
        'console_scripts': [
            'yumemi=yumemi.cli:main'
        ],
    },
)
