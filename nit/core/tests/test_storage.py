#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory

from nit.core.tests.util import NitTestCase
from nit.components.nit.storage import NitStorage
from nit.core.blob import Blob


class TestNitStorage(NitTestCase):

    """
    """

    def test_blob_should_get_the_same_string_it_puts(self):
        """
        """

        with TemporaryDirectory() as project_dir_path:
            self.assertDirExists(project_dir_path)

            test_str = "This is only a test\n"

            from nit.core.paths import BasePaths

            paths = BasePaths(project_dir_path)

            storage = NitStorage(paths)
            storage.create()

            test_blob = Blob(test_str.encode())
            key = storage.put(test_blob)

            actual_blob = storage.get_object(key)
            assert actual_blob.content.decode() == test_str

        self.assertNotDirExists(project_dir_path)
