#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This app-generic Git version-check (gitvck) module is used
            to test this module's version against the latest version in
            the defined (network-local) Git repository.

            If this version number is behind the version number in Git,
            the user is notified on import.

            Note:
                This tool uses **git tags** to determine the
                repository's version. Therefore, the git repository must
                be tagged with a version number following the convention
                defined in the 'Version scheme' section of PEP-440.
                For example::

                    vX.Y.Z[ ... ]

                Refer to
                https://www.python.org/dev/peps/pep-440/#version-scheme
                for further detail.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Deployment:

            On deployment, add this to the main package's primary
            ``__init__.py`` file::

                from gitvck import gitvck
                from ._version import __version__

                # Compare version numbers on import.
                gitvck.VersionCheck(name='project-spam',
                                    version=__version__,
                                    path='/path/to/git/project-spam').test()

:Comments:  n/a

"""
# pylint: disable=import-error
# pylint: disable=wrong-import-order

import os
import re
import subprocess as sp
from packaging import version as pkgversion
from utils4.user_interface import ui


class VersionCheck:
    """Compare this version against the version in the git repository.

    Args:
        name (str): Name of the project. Used only for the displayed
            message.
        version (str): Version of the project.
        path (str): Explicit path to the project's Git repository to be
            tested. This repository must be local to the network.

    Note:
        This class is simply a *warning* mechanism. Processes are not
        stoppednor prevented. If the version test fails, the user is
        simply warned.

    """

    def __init__(self, name: str, version: str, path: str):
        """VersionCheck class initialiser."""
        self._name = name
        self._v = version
        self._path = path
        self._gitv = ''

    def test(self):
        """Test the version numbers between this library and the Git repo.

        If a version tag could not be parsed from the Git repo, the
        user is alerted and no further action is taken.

        If the version of this library is *behind* the git repository,
        the user is alerted. Otherwise, no further action is taken.

        """
        self._get_git_version()
        if not self._gitv:
            self._alert_not_found()
        else:
            if pkgversion.parse(self._v) < pkgversion.parse(self._gitv):
                self._alert()

    def _alert(self):
        """Alert the user that a new version is available."""
        msg = (f'\nNote: A later version of {self._name} is available.\n'
               f'- Installed version: {self._v}\n'
               f'- Repo version: {self._gitv}\n')
        ui.print_warning(msg)

    def _alert_not_found(self):
        """Alert the user that a Git tag could not be parsed."""
        msg = ('\nA version tag could not be parsed from the following Git repo:\n'
               f'- {self._path}\n'
               '\nVersion not checked.\n')
        ui.print_alert(msg)

    def _get_git_version(self):
        """Get the latest version number from git."""
        v = ''
        exp = re.compile('^v(.*)$')
        if os.path.exists(self._path):
            cmd = ['git', 'describe', '--tags']
            with sp.Popen(cmd, cwd=self._path, stdout=sp.PIPE) as proc:
                stdout, _ = proc.communicate()
                if not proc.returncode:
                    v = exp.findall(stdout.decode().strip())[0]
        self._gitv = v
