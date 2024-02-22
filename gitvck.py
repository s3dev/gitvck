#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This app-generic Git version-check (gitvck) module is used to
            test this module's version against the latest version in the
            defined git repository.

            If this version number is behind the version number in git,
            the user is notified on import.

            Note:
                This tool uses **git tags** to determine the repository's
                version. Therefore, the git repository must be tagged with a
                version number following the convention defined in the
                'Version scheme' section of PEP-440.  For example::

                    vX.Y.Z[ ... ]

                Refer to
                https://www.python.org/dev/peps/pep-440/#version-scheme
                for further detail.

:Platform:  Linux/Windows | Python 3.8
:Developer: J Berendt
:Email:     support@s3dev.uk

:Deployment:

            #. On deployment, add this to the main package's
               ``__init__.py`` file::

                from ._version import __version__
                from .<package> import gitvck

                # Compare version numbers on import.
                gitvck.VersionCheck(__version__).test()

            #. Update the local :class:`~_Config` class to align with the
               app.

:Comments:  n/a

"""
# pylint: disable=invalid-name
# pylint: disable=subprocess-run-check

import os
import re
import socket
from subprocess import run, PIPE
from packaging import version
from utils4.user_interface import ui


class _Config:
    """Base configuration class for the :class:`~VersionCheck` class.

    Note:
        These items are to be updated for the specific app.

    """

    _HST = socket.gethostname().lower()
    PKG = ''
    REPO = ''


class VersionCheck(_Config):
    """Compare this version against the version in the git repository.

    Args:
        v (str): Version of the local library.

    Note:
        This class is simply a *warning* mechanism. Processed are not stopped
        nor prevented. If the version test fails, the user is simply warned.

    """

    def __init__(self, v: str):
        """VersionCheck class initialiser."""
        self._v = v
        self._git = self._git_version()

    def test(self):
        """Test the version numbers between this library and the git repository.

        The the version of this library is *behind* the git repository, the
        user is alerted. Otherwise, no further action is taken.

        """
        if version.parse(self._v) < version.parse(self._git):
            self._alert()

    def _alert(self):
        """Alert the user that a new version is available."""
        msg = ('\nNote: A later version of {} is available.\n'
               '- Installed version: {}\n'
               '- Repo version: {}\n')
        msg = msg.format(self.PKG, self._v, self._git)
        ui.print_warning(msg)

    def _git_version(self):
        """Get the latest version number from git."""
        v = ''
        exp = re.compile('^v(.*)$')
        if os.path.exists(self.REPO):
            cmd = ['git', 'describe', '--tags']
            p = run(cmd, cwd=self.REPO, stdout=PIPE)
            if not p.returncode:
                v = exp.findall(p.stdout.decode().strip())[0]
        return v
