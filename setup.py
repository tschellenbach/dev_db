#!/usr/bin/env python
from setuptools import setup, find_packages
from dev_db import __version__, __maintainer__, __email__


DESCRIPTION = """Tool to automatically create a development database for local development by sampling your production database.
It maintains referential integrity by looking up the dependencies for the selected rows.
"""


tests_require = [
    'mock',
    'pep8',
    'coverage',
    'unittest2',
]

install_requires = [
    'django',
]

license_text = open('LICENSE.txt').read()
long_description = open('README.md').read()
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='dev_db',
    version=__version__,
    author=__maintainer__,
    author_email=__email__,
    license=license_text,
    url='http://github.com/tschellenbach/dev_db',
    description=DESCRIPTION,
    long_description=long_description,
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='dev_db.tests',
    include_package_data=True,
    classifiers=CLASSIFIERS,
)
