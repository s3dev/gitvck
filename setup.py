#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:App:       setup.py
:Purpose:   Python library packager.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Example:
    Create source and wheel distributions::

        $ cd /path/to/package
        $ python setup.py sdist bdist_wheel

    Simple installation::

        $ cd /path/to/package/dist
        $ pip install <pkgname>-<...>.whl

    git installation::

        $ pip install git+file:///<drive>/path/to/package

    github installation::

        $ pip install git+https://github.com/s3dev/<pkgname>

"""
# pylint: disable=invalid-name

import os
from setuptools import setup
from gitvck._version import __version__


class Setup:
    """Create a dist package for this library."""

    PACKAGE         = 'gitvck'
    VERSION         = __version__
    PLATFORMS       = 'Python 3.6+'
    DESC            = 'A simple Git repository version checker for your project.'
    AUTHOR          = 'J. Berendt'
    AUTHOR_EMAIL    = 'support@s3dev.uk'
    URL             = ''
    LICENSE         = 'MIT'
    ROOT            = os.path.realpath(os.path.dirname(__file__))
    PACKAGE_ROOT    = os.path.join(ROOT, PACKAGE)
    DIST            = os.path.join(ROOT, 'dist')
    INCL_PKG_DATA   = False
    MIN_PYTHON      = '>=3.6'
    CLASSIFIERS     = ['Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Programming Language :: Python :: 3.8',
                       'Programming Language :: Python :: 3.9',
                       'Programming Language :: Python :: 3.10',
                       'Programming Language :: Python :: 3.11',
                       'Programming Language :: Python :: 3.12',
                       'License :: OSI Approved :: MIT License',
                       'Development Status :: 4 - Beta',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX :: Linux',
                       'Topic :: Software Development',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities']

    # PACKAGE REQUIREMENTS
    PACKAGES        = ['gitvck']
    REQUIRES        = ['packaging', 'utils4']

    def run(self):
        """Run the setup."""
        setup(name=self.PACKAGE,
              version=self.VERSION,
              platforms=self.PLATFORMS,
              python_requires=self.MIN_PYTHON,
              description=self.DESC,
              author=self.AUTHOR,
              author_email=self.AUTHOR_EMAIL,
              maintainer=self.AUTHOR,
              maintainer_email=self.AUTHOR_EMAIL,
              url=self.URL,
              license=self.LICENSE,
               packages=self.PACKAGES,
              install_requires=self.REQUIRES,
              include_package_data=self.INCL_PKG_DATA,
              classifiers=self.CLASSIFIERS,
             )


if __name__ == '__main__':
    Setup().run()
