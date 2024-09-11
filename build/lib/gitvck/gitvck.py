#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This project-generic Git version-check (gitvck) module is
            used to test your project's version against the latest
            version available in source configuration.

            The version can be checked against PyPI, GitHub or even a
            local (offline) Git repository.

            If the project's version number is behind the version number
            obtained from the source, the user is notified on import, as
            a **notification-only** service. This check is *not* designed
            to prevent the user from carrying on.

            .. important::

                **A note for using a Git(Hub) repository:**

                When comparing version against a Git repository, this
                tool uses **tags** to determine the project's version.
                Therefore, the tag on the release must be the version
                number and follow the convention defined in the
                *Version scheme* section of `PEP-440`_.

                For example::

                    [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

                Public version identifiers are separated into up to five
                segments:

                    - Epoch segment: N!
                    - Release segment: N(.N)*
                    - Pre-release segment: {a|b|rc}N
                    - Post-release segment: .postN
                    - Development release segment: .devN

            .. _PEP-440: https://www.python.org/dev/peps/pep-440/#version-scheme

:Platform:  Linux/Windows | Python 3.8+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Deployment:

            On deployment, simply copy/paste one of the following code
            examples into the project's primary ``__init__.py`` module.
            When the project is imported, the ``__init__.py`` module is
            run, thus executing the version check.

:Examples:

            Check the version against a *local Git repository*::

                from gitvck import gitvck
                from <project>._version import __version__

                gitvck.VersionCheck(name='project-spam',
                                    source='git',
                                    path='/path/to/git/project-spam',
                                    version=__version__).test()


            Check the version against *GitHub*::

                from gitvck import gitvck
                from <project>._version import __version__

                gitvck.VersionCheck(name='project-spam',
                                    source='git',
                                    path='https://github.com/s3dev/project-spam',
                                    version=__version__).test()


            Check the version against *PyPI*::

                from gitvck import gitvck
                from <project>._version import __version__

                gitvck.VersionCheck(name='project-spam',
                                    source='pypi',
                                    version=__version__).test()


            Check the version against *PyPI*, using the version from the
            *installed* library.

            Notice the template below passes ``None`` into the
            ``version`` argument. This instructs ``gitvck`` to collect
            the internal version from the *installed* library using
            ``importlib``, rather than from the local project's
            ``_version.py`` file.

            This variation can be used with any of the templates above::

                from gitvck import gitvck

                gitvck.VersionCheck(name='project-spam',
                                    source='pypi',
                                    version=None).test()

"""
# pylint: disable=wrong-import-order

import packaging.version as pkgversion  # Required to address packaging import 'bug'.
import requests
import subprocess as sp
import traceback
from importlib import metadata
from utils4.user_interface import ui


class VersionCheck:
    """Compare a project's version against the version in source
    configuration.

    Args:
        name (str): Name of the project.
        source (str): Source against which the version is checked.
            Options: 'git' or 'pypi'. If 'git', the ``path`` argument
            must be populated. If 'pypi', the ``name`` argument is used
            to query the PyPI register.
        path (str, optional): Explicit path to the project's local Git
            repository, or the GitHub URL to the project. If referencing
            PyPI, this can be left as ``None``. Defaults to None.
        version (str, optional): Version of the project.
            If the version of the *installed* library is to be tested,
            this argument should be left as ``None``. Otherwise, the
            ``__version__`` variable from the project's ``_version.py``
            file can be used. Defaults to None.

    .. note::

        This class is simply a *warning* mechanism. Processes are not
        stopped nor prevented, once preliminary internal checks pass. If
        the version test fails, the user is simply warned and allowed to
        carry on.

    """

    _SOURCES = ('git', 'pypi')

    def __init__(self, name: str, source: str, path: str=None, version: str=None):
        """VersionCheck class initialiser."""
        self._name = name
        self._src = source.lower()
        self._path = path
        self._vers = version  # Project version.
        self._extvers = None  # Version obtained from Git or PyPI.

    def test(self) -> bool:
        """Test the version numbers between the library and its source.

        If the version of the library is *behind* the source, the user
        is alerted. Otherwise, no further action is taken.

        The following processing steps are carried out by this test:

            - Verify the arguments are valid.
            - Get the version number for the internal project.
            - Get the version number from the project's configured
              source.
            - Verify the two version numbers are valid per PEP-440.
            - Compare the internal and external version numbers.
            - Notify the user if the version of the library is behind
              the source.

        Returns:
            bool: True if the versions compared successfully and the
            source is not ahead of the tested library, otherwise False.
            The return value is used by the testing suite.

        """
        # pylint: disable=multiple-statements
        try:
            s = False
            if self._verify_args():
                s = self._get_version_internal()
                if s: s = self._get_version_external()
                if s: s = self._verify_version_numbers()
                if s: s = self._compare()
        except Exception:
            print('', traceback.format_exc(), sep='\n')
        return s

    def _compare(self) -> bool:
        """Compare the internal and external version numbers.

        Returns:
            bool: False if the internal version is behind (less than)
            the external version. Otherwise, True.

        """
        if pkgversion.parse(self._vers) < pkgversion.parse(self._extvers):
            self._new_version_available()
            return False
        return True

    def _get_version_external(self):
        """Get the version from the specified external source.

        :Key:

            - **git**: Use the ``path`` argument to obtain and parse the
              latest *tag* from Git(Hub).
            - **pypi**: Use the ``name`` argument to query PyPI for the
              latest version held.

        The collected version is stored into the :attr:`~_extvers`
        attribute by the appropriate collection method:

            - :meth:`~_get_version_from_git`
            - :meth:`~_get_version_from_pypi`

        Returns:
            bool: True if the :attr:`~_extvers` attribute is now
            populated. Otherwise, False.

        """
        if self._src == 'git':
            self._get_version_from_git()
        elif self._src == 'pypi':
            self._get_version_from_pypi()
        if self._extvers is None:
            msg = f'\n[ERROR]: The external version for \'{self._name}\' could not be found.'
            ui.print_warning(msg)
            return False
        return True

    def _get_version_from_git(self):
        """Collect and parse the latest tag from Git(Hub).

        To obtain the tag(s), the ``git ls-remote`` command is used.

        .. important::

            This method relies on the version number being the commit's
            *tag*, and follows the versioning scheme found in PEP-440.

        """
        cmd = ['git', 'ls-remote', '--tags', '--refs', '--sort=version:refname', self._path]
        with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE) as proc:
            stdout, stderr = proc.communicate()
            if not proc.returncode:
                self._parse_git_output(data=stdout)
            else:
                ui.print_warning(f'\nGit error:\n{stderr.decode()}')

    def _get_version_from_pypi(self):
        """Collect and parse the latest tag from PyPI.

        .. important::

            This method queries the PyPI register and returns the version
            of the *latest* project.

        """
        URI = f'https://pypi.org/pypi/{self._name}/json'
        with requests.get(URI, timeout=5) as r:
            if r.status_code == 200:
                self._extvers = r.json()['info']['version']

    def _get_version_internal(self) -> bool:
        """Collect the project's version to be compared.

        If the ``version`` argument is ``None``, the version for the
        *installed* project is obtained using ``importlib.metadata``.
        Otherwise, the string provided to the ``version`` argument is
        used.

        The internal version is stored into the :attr:`~_vers` attribute.

        Returns:
            bool: True if the :attr:`~_vers` attribute is now populated.
            Otherwise, False.

        """
        if self._vers is None:
            try:
                v = metadata.version(self._name)
                if self._version_is_valid(version=v):
                    self._vers = v
            except metadata.PackageNotFoundError:
                msg = (f'\n[ERROR]: The \'{self._name}\' project is not installed. '
                       'Cannot collect version information.')
                ui.print_warning(msg)
        return self._vers is not None

    def _new_version_available(self):
        """Alert the user that a new version is available."""
        msg = (f'\nNote: A later version of {self._name} is available.\n'
               f'- Installed version: {self._vers}\n'
               f'- Repo version: {self._extvers}\n')
        ui.print_warning(msg)

    def _parse_git_output(self, data: bytes):
        """Parse the output from the ``git ls-remote`` command.

        To keep the project OS-agnostic, the parsing of the tag
        collection command is parsed here, rather than during the
        subprocess session.

        Specifically, this method extracts the last field from the last
        line of output. This will be the latest tag from the Git
        repository.

        The tag (hopefully a version!) is stored into the
        :attr:`~_extvers` attribute. Before the versions are compared,
        the version is verified by the :meth:`~_verify_version_numbers`
        method, in the event the tag is not a version number.

        Args:
            data (bytes): Bytestring returned from the sub-process
                call's ``stdout`` stream.

        """
        # Remove any empty lines.
        data_ = list(filter(None, data.decode().split('\n')))
        if data_:
            latest = data_[-1]
            self._extvers = latest.split('/')[-1]

    def _verify_args(self) -> bool:
        """Verify the class arguments are valid.

        Raises:
            RuntimeError: Raised if the provided source is invalid, or
                a source of 'git' is provided and the ``path`` argument is
                ``None``.

        Returns:
            bool: True if the arguments are valid, otherwise a
            RuntimeError is raised.

        """
        if not self._src in self._SOURCES:
            raise RuntimeError(f'Invalid source argument provided: \'{self._src}\'')
        if self._src == 'git' and self._path is None:
            raise RuntimeError('A path argument must be provided for a \'git\' source.')
        return True

    def _verify_version_numbers(self) -> bool:
        """Verify the version numbers are valid according to PEP-440.

        Both the internal and external version numbers are tested.

        Returns:
            bool: True if *both* version numbers are valid, otherwise
            False.

        """
        return all((self._version_is_valid(version=self._vers),
                    self._version_is_valid(version=self._extvers)))

    @staticmethod
    def _version_is_valid(version: str) -> bool:
        """Verify a version string is valid.

        :Implementation:
            This test calls the :func:`packaging.version.parse` function,
            wrapped in a ``try/except`` block, to verify the version
            string.

        Args:
            version (str): Version string to be tested.

        Returns:
            bool: True if the version string is valid, otherwise False.

        """
        try:
            pkgversion.parse(version)
            return True
        except pkgversion.InvalidVersion:
            msg = f'\n[ERROR]: The following version number is invalid: \'{version}\''
            ui.print_warning(msg)
            return False
