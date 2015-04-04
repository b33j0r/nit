#! /usr/bin/env python
"""
"""
from nit.core.tests.util import NitTestCase
from nit.core.storage import NitStorage, NitBlob

class TestBlobStorage(NitTestCase):

    """
    """

    def test_blob_should_get_the_same_string_it_puts(self):
        """
        """

        test_str = "This is only a test\n"

        project_dir_path = "/Users/brjorgensen/nit_test_proj"
        storage = NitStorage(project_dir_path)
        storage.create(force=True)

        test_blob = NitBlob(test_str.encode())
        storage.put(test_blob)

        actual_blob = storage.get(test_blob.key)
        assert actual_blob.content.decode() == test_str
