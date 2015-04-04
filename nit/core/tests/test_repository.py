#! /usr/bin/env python
"""
"""
import os
from nit.core.objects import BaseBlob
from nit.core.repository import Repository
from nit.core.tests.util import NitTestCase


class TestRepository(NitTestCase):
    """
    """
    def setUp(self):
        self.project_dir_path = "/Users/brjorgensen/nit_test_proj"
        self.repo = Repository(self.project_dir_path)
        self.repo.destroy()

    def test_init_should_create_a_repo(self):
        """
        """
        self.repo.init()
        self.assertDirExists(self.repo.storage.repo_dir_path)

    def test_init_should_fail_if_repo_exists(self):
        """
        """
        self.repo.init()
        with self.expectUserError():
            self.repo.init()

    def test_init_should_not_fail_if_repo_exists_and_force_is_true(self):
        """
        """
        self.repo.init()
        self.repo.init(force=True)
