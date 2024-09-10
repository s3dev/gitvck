============================
gitvck Library Documentation
============================

.. contents:: Page Contents
    :local:
    :depth: 1

Overview
========
The ``gitvck`` library is a CPython project which is designed to help
ensure the latest version of a critical library is being used by your
project.

Sometimes a project relies on the *latest* version of an underlying 
library. The ``gitvck`` library is designed to run in the background on
program startup and check if the version of a critical library is the 
latest version available. If the critical library being imported is not
the latest, the user is alerted that a later version is available. If the
latest version is already being used, the test ends silently.

However, this is a *notification-only* service. The user is *not*
prevented from carrying on.

If you have any questions that are not covered by this documentation, or
if you spot any bugs, issues or have any recommendations, please feel free
to :ref:`contact us <contact-us>`.


Installation
============
The easiest way to install ``gitvck`` from `PyPI`_ is using ``pip``
*after* activating your virtual environment::
    
    pip install gitvck


.. _using-the-library:

Using the Library
=================
This documentation suite contains detailed explanation and example usage 
for each of the library's importable modules. For detailed documentation, 
usage examples and links the source code itself, please refer to the 
:ref:`library-api` page.

If there is a specific module or method which you cannot find, a 
**search** field is built into the navigation bar to the left.

Quickstart
----------
To demonstrate how easy it is to get up and running, the template below
can be copied and pasted into your program's primary ``__init__.py`` 
module. When your program starts up, the ``__init__.py`` module is run,
and performs the version check in the background.

To verify the version of a critical library against GitHub use::

    from gitvck import gitvck
    from <project>._version import __version__

    gitvck.VersionCheck(name='project-spam',
                        source='git',
                        path='https://github.com/s3dev/project-spam',
                        version=__version__).test()

More example templates can be found in the ``gitvck`` module documentation
on the :ref:`library-api` page.

Sources
-------
The following code configuration sources can be accessed by ``gitvck``:

- PyPI
- GitHub
- Git (a local or remote repository, accessed through a filesystem)

Guidance for using these various sources can be found in the ``gitvck``
module documentation on the :ref:`library-api` page.


.. _troubleshooting:

Troubleshooting
===============
No guidance at this time.


Documentation Contents
======================
.. toctree::
    :maxdepth: 1

    library
    changelog
    contact


Indices and Tables
==================
* :ref:`genindex`
* :ref:`modindex`


.. rubric:: Footnotes

.. _PyPI: https://pypi.org/project/gitvck

|lastupdated|

