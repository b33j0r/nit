#! /usr/bin/env python
"""
"""
import os
from contextlib import contextmanager
from unittest import TestCase

from nit.core.errors import NitUserError


class NitTestCase(TestCase):

    """
    """

    @contextmanager
    def expectUserError(self, msg="No exception was raised"):
        try:
            yield
        except NitUserError:
            pass
        else:
            raise AssertionError(msg)

    def assertDirExists(self, dir_path):
        self.assertTrue(os.path.exists(dir_path))
        self.assertTrue(os.path.isdir(dir_path))

    def assertNotDirExists(self, dir_path):
        self.assertFalse(os.path.exists(dir_path))
