from setuptools import setup
from os import path
import re


version = None
with open(path.join('yumemi', '__init__.py')) as f:
    version_cre = re.compile(
        r'^__version__\s+=\s+[\'"](?P<version>\d+\.\d+.*)[\'"]$'
    )
    for line in f:
        match = version_cre.match(line)
        if match:
            version = match.group('version')
            break

with open('README.rst') as f:
    long_description = f.read()


setup(
    name='yumemi',
    version=version,
    description='AniDB library and simple CLI client.',
    long_description=long_description,
    author='Filip Pobořil',
    author_email='tsuki@fpob.cz',
    url='https://gitlab.com/fpob/yumemi',
    download_url='https://gitlab.com/fpob/yumemi/-/archive/v{v}/yumemi-v{v}.zip'.format(v=version),
    license='MIT',
    keywords=['AniDB'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    packages=['yumemi'],
    python_requires='>=3.6',
    install_requires=['click', 'python-dateutil'],
    extras_require={
        'encrypt': ['pycrypto'],
    },
    entry_points={
        'console_scripts': [
            'yumemi=yumemi.cli:main'
        ],
    },
)
