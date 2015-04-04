#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory

from nit.components.nit.repository import NitRepository
from nit.core.tests.util import NitTestCase


class TestNitRepository(NitTestCase):
    """
    """
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.project_dir_path = self.temp_dir.name
        self.repo = NitRepository(self.project_dir_path)
        self.repo.destroy()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_should_create_a_repo(self):
        """
        """
        self.repo.create()
        self.assertDirExists(self.repo.storage.repo_dir_path)

    def test_create_should_fail_if_repo_exists(self):
        """
        """
        self.repo.create()
        with self.expectUserError():
            self.repo.create()

    def test_create_should_not_fail_if_repo_exists_and_force_is_true(self):
        """
        """
        self.repo.create()
        self.repo.create(force=True)
