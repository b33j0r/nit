#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory

from nit.core.tests.util import NitTestCase
from nit.components.nit.storage import NitStorage
from nit.components.nit.blob import NitBlob


class TestNitStorage(NitTestCase):

    """
    """

    def test_blob_should_get_the_same_string_it_puts(self):
        """
        """

        with TemporaryDirectory() as project_dir_path:
            self.assertDirExists(project_dir_path)

            test_str = "This is only a test\n"

            storage = NitStorage(project_dir_path)
            storage.create()

            test_blob = NitBlob(test_str.encode())
            storage.put(test_blob)

            actual_blob = storage.get(test_blob.key)
            assert actual_blob.content.decode() == test_str

        self.assertNotDirExists(project_dir_path)
