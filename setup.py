from setuptools import setup
from os import path

import yumemi


__dir__ = path.abspath(path.dirname(__file__))


with open(path.join(__dir__, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='yumemi',
    version=yumemi.__version__,
    description='AniDB library and simple CLI client.',
    long_description=long_description,
    author='Filip Pobořil',
    author_email='tsuki@fpob.eu',
    url='https://github.com/fpob/yumemi',
    download_url='https://github.com/fpob/yumemi/archive/v{}.tar.gz'.format(yumemi.__version__),
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    packages=['yumemi'],
    install_requires=['click'],
    extras_require={
        'encrypt': ['pycrypto'],
    },
    entry_points={
        'console_scripts': [
            'yumemi=yumemi.cli:main'
        ],
    },
)
