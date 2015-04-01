#! /usr/bin/env python
"""
"""
from contextlib import contextmanager

import os

from unittest import TestCase
from nit.core.errors import NitUserError


class NitTestCase(TestCase):
    """
    """

    @contextmanager
    def expectUserError(self, msg=None):
        try:
            yield
        except NitUserError:
            pass
        else:
            raise AssertionError(msg)

    def assertDirExists(self, dir_path):
        self.assertTrue(os.path.exists(dir_path))
        self.assertTrue(os.path.isdir(dir_path))
