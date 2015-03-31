#! /usr/bin/env python
"""
"""
import os
from unittest import TestCase
from nit.core.objects import BaseBlob
from nit.core.repository import Repository
from nit.core.storage import NitStorageStrategy

class TestBlobStorage(TestCase):
    """
    """
    def test_blob_should_get_the_same_string_it_puts(self):
        test_str = "This is only a test"

        project_dir_path = "/Users/brjorgensen/nit_test_proj"
        storage = NitStorageStrategy(project_dir_path)
        storage.init(force=True)

        test_blob = BaseBlob(test_str.encode())
        storage.put_blob(test_blob)

        actual_blob = BaseBlob.get(storage, test_blob.key)
        assert actual_blob.content.decode() == test_str