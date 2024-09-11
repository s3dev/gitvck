#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Perform automated testing on the ``gitvck`` module.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

"""
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=wrong-import-position

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# Set sys.path for relative imports ^^^
import contextlib
import io
import subprocess as sp
# locals
from base import TestBase
from testlibs import msgs
from gitvck import gitvck


class TestGitVCK(TestBase):
    """Testing suite for the ``gitvck`` module."""

    _FILE = os.path.splitext(os.path.basename(__file__))[0]
    _MSG1 = msgs.templates.not_as_expected.general

    @classmethod
    def setUpClass(cls):
        """Run this logic at the start of all test cases."""
        msgs.startoftest.startoftest(module_name='gitvck')

    def test01a__test_pypi_w_version(self):
        """Test the ``test`` method for a PyPI source.

        :Test:
            - Verify the installed version of ``utils4`` against PyPI.
              The version is intentionally hard-coded to pass this test.

        """
        tst = gitvck.VersionCheck(name='utils4',
                                  source='pypi',
                                  version='99.99.99').test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test01b__test_pypi_wo_version(self):
        """Test the ``test`` method for a PyPI source.

        :Test:
            - Verify the installed version for ``utils4`` against PyPI.
              This is assumed to always be up-to-date, especially in a
              development environment.

        """
        tst = gitvck.VersionCheck(name='utils4',
                                  source='pypi',
                                  version=None).test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test02a__test_git_w_version(self):
        """Test the ``test`` method for a local Git source.

        :Test:
            - Verify a local Git source, using the path to *this project*.
              The version is intentionally hard-coded to pass this test.

        """
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        tst = gitvck.VersionCheck(name='gitvck',
                                  source='git',
                                  path=path,
                                  version='99.99.99').test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test02b__test_git_wo_version(self):
        """Test the ``test`` method for a local Git source.

        :Test:
            - Verify the installed version for ``gitvck`` against a path
              to *this project*. See note.

        .. note::

            This test may prove tricky, because it uses Git tags from
            *this project*, and references the *installed* version of
            ``gitvck``. These may (in some testing cases) be out of sync.

        """
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        tst = gitvck.VersionCheck(name='gitvck',
                                  source='git',
                                  path=path,
                                  version=None).test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test03a__test_git_w_version(self):
        """Test the ``test`` method for a GitHub source.

        :Test:
            - Verify the GitHub version for ``utils4``. The version is
              intentionally hard-coded to pass this test.

        """
        tst = gitvck.VersionCheck(name='utils4',
                                  source='git',
                                  path='https://github.com/s3dev/utils4',
                                  version='99.99.99').test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test03b__test_git_wo_version(self):
        """Test the ``test`` method for a GitHub source.

        :Test:
            - Verify the installed version for ``utils4`` against GitHub.
              This is assumed to always be up-to-date, especially in a
              development environment.


        """
        tst = gitvck.VersionCheck(name='utils4',
                                  source='git',
                                  path='https://github.com/s3dev/utils4',
                                  version=None).test()
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test04a___compare__new_version_available(self):
        """Test the ``_compare`` method for a GitHub source.

        :Test:
            - For a GitHub repo, trigger the 'later version available'
              terminal messages for ``utils4``.
            - Verify the appropriate messages are displayed to the
              terminal.
            - An old version number is intentionally hard-coded to
              trigger the message.

        """
        buf = io.StringIO()
        lib = 'utils4'
        v1 = '0.1.0'
        v2 = self.get_version_from_github(lib=lib)
        with contextlib.redirect_stdout(buf):
            tst1 = gitvck.VersionCheck(name=lib,
                                       source='git',
                                       path=f'https://github.com/s3dev/{lib}',
                                       version=v1).test()
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn(f'A later version of {lib} is available', tst2[0])
        self.assertIn(f'Installed version: {v1}', tst2[1])
        self.assertIn(f'Repo version: {v2}', tst2[2])

    def test05a___get_version_from_git__invalid_repo(self):
        """Test the ``_get_version_from_git`` method for an invalid repo.

        :Test:
            - Test a local Git repository with an invalid path.
            - Verify the appropriate messages are displayed to the
              terminal.

        """
        buf = io.StringIO()
        lib = 'utilsX'
        v = '0.1.0'
        with contextlib.redirect_stdout(buf):
            tst1 = gitvck.VersionCheck(name=lib,
                                       source='git',
                                       path='../..',
                                       version=v).test()
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn('Git error', tst2[0])
        self.assertIn('fatal:', tst2[1])
        self.assertIn(f'external version for \'{lib}\' could not be found', tst2[-1])

    def test06a___get_version_internal__invalid_project(self):
        """Test the ``_get_version_internal`` method for an invalid project.

        :Test:
            - Verify the appropriate error message is displayed when a
              non-installed project is requested, with ``version=None``.

        """
        buf = io.StringIO()
        lib = 'utilsX'
        with contextlib.redirect_stdout(buf):
            tst1 = gitvck.VersionCheck(name=lib,
                                       source='git',
                                       path='..',
                                       version=None).test()
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn(f'The \'{lib}\' project is not installed', tst2[0])

    def test07a__args__invalid_source(self):
        """Test the class arguments with an invalid source.

        :Test:
            - Run a check with an invalid source argument.
            - Verify the appropriate message is displayed to the
              terminal.

        """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tst1 = gitvck.VersionCheck(name='gitvck',
                                       source='invalid',
                                       version=None).test()
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn('Traceback', tst2[0])
        self.assertIn('RuntimeError: Invalid source argument', tst2[-1])

    def test07b__args__missing_path(self):
        """Test the class arguments with a missing path.

        :Test:
            - Run a check with a missing path argument for 'git'.
            - Verify the appropriate message is displayed to the
              terminal.

        """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tst1 = gitvck.VersionCheck(name='gitvck',
                                       source='git',
                                       version=None).test()
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn('Traceback', tst2[0])
        self.assertIn('RuntimeError: A path argument must be provided', tst2[-1])

    def test08a___version_is_valid__valid(self):
        """Test the ``_version_is_valid`` method with a valid version.

        :Test:
            - Pass a valid version number into the method and verify the
              return is True.

        """
        vc = gitvck.VersionCheck(name='gitvck',
                                 source='pypi',
                                 version=None)
        tst = vc._version_is_valid('1.2.3')
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test08b___version_is_valid__invalid(self):
        """Test the ``_version_is_valid`` method with an invalid version.

        :Test:
            - Pass an invalid version number into the method and verify
              the return is False.
            - Verify the appropriate message is displayed to the
              terminal.

        """
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            vc = gitvck.VersionCheck(name='gitvck',
                                     source='pypi',
                                     version=None)
            tst1 = vc._version_is_valid('1.abc.1')
            text = buf.getvalue()
        # Clean stdout and split the text into lines.
        tst2 = list(filter(None, ''.join(self.strip_ansi_colour(text)).split('\n')))
        self.assertFalse(tst1, msg=self._MSG1.format(False, tst1))
        self.assertIn('The following version number is invalid', tst2[0])

#%% Helpers

    def get_version_from_github(self, lib: str) -> str:
        """Get the latest tag from GitHub.

        Args:
            lib (str): Library (project) to be queried.

        Returns:
            str: The tag (version) from GitHub.

        """
        cmd = ['git',
               'ls-remote',
               '--tags',
               '--refs',
               '--sort=version:refname',
               f'https://github.com/s3dev/{lib}']
        v = None
        with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE) as proc:
            stdout, _ = proc.communicate()
            if not proc.returncode:
                data = stdout.decode()
                latest = list(filter(None, data.split('\n')))[-1]
                v = latest.split('/')[-1]
        return v
