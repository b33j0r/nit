#! /usr/bin/env python
"""
"""
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import mock

from nit.components.nit.serialization import NitSerializer
from nit.core.objects.commit import Commit
from nit.core.paths import BasePaths
from nit.core.serialization import BaseSerializer
from nit.components.base.storage import BaseStorage
from nit.core.tests.util import NitTestCase


class TestBaseStorageCreation(NitTestCase):

    """
    """

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.paths = BasePaths(self.temp_dir.name, verify=False)
        self.storage = BaseStorage(self.paths)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_not_exists(self):
        """
        """
        assert not self.storage.exists

    def test_create(self):
        """
        """
        self.storage.create()
        assert self.storage.exists
        assert isinstance(self.storage.paths.repo, Path)
        assert self.storage.paths.repo.exists()

    def test_destroy(self):
        """
        """
        self.storage.create()
        self.storage.destroy()
        assert not self.storage.exists
        assert isinstance(self.storage.paths.repo, Path)
        assert not self.storage.paths.repo.exists()


class TestBaseStorage(NitTestCase):

    """
    """

    SERIALIZATION_CLS = BaseSerializer

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.paths = BasePaths(self.temp_dir.name, verify=False)
        self.storage = BaseStorage(
            self.paths,
            serialization_cls=self.SERIALIZATION_CLS
        )
        self.storage.create()

    def tearDown(self):
        self.storage.destroy()
        self.temp_dir.cleanup()

    def test_exists(self):
        """
        """
        assert self.storage.exists
        assert self.storage.paths.repo.exists()
        assert self.storage.paths.refs.exists()
        assert self.storage.paths.objects.exists()

    @mock.patch("nit.core.objects.blob.Blob")
    def test_put_calls_accept_put(self, MockBlob):
        mock_blob = MockBlob()
        self.storage.put(mock_blob)
        mock_blob.accept_put.assert_called_with(self.storage)

    def test_put_symbolic_ref(self):
        head_path = self.storage.paths.repo/"HEAD"

        assert not head_path.exists()

        self.storage.put_symbolic_ref("HEAD", "origin/master")

        assert head_path.exists()

        with head_path.open('rb') as file:
            b = file.read()
            assert b.decode() == "origin/master"

    def test_get_symbolic_ref(self):
        ref = "origin/master"
        head_path = self.storage.paths.repo/"HEAD"
        with head_path.open('wb') as file:
            b = ref.encode()
            file.write(b)

        self.storage.get_symbolic_ref("HEAD")

        with head_path.open('rb') as file:
            b = file.read()
            assert b.decode() == "origin/master"

    def test_put_ref(self):
        ref_path = self.storage.paths.refs/"origin/master"

        assert not ref_path.exists()

        self.storage.put_ref("origin/master", "aaaa")

        assert ref_path.exists()

        with ref_path.open('rb') as file:
            b = file.read()
            assert b.decode() == "aaaa"

    def test_get_ref(self):
        ref_path = self.storage.paths.refs/"origin/master"
        ref_path.parent.mkdir(parents=True)
        with ref_path.open('wb') as file:
            b = "aaaa".encode()
            file.write(b)

        with ref_path.open('rb') as file:
            b = file.read()
            assert b.decode() == "aaaa"

        ref_key = self.storage.get_ref("origin/master")
        assert ref_key == "aaaa"


class TestNitStorage(TestBaseStorage):

    """
    """

    SERIALIZATION_CLS = NitSerializer

    # @skip("Not Implemented")
    # def test_put_blob(self):
    #     assert False
    #
    # @skip("Not Implemented")
    # def test_get_blob(self):
    #     assert False

    def test_get_commit(self):
        commit = Commit("aaaa", "bbbb", message="cccc")
        content = self.storage._serialize_object_to_bytes(commit)
        print("content: {}".format(content))
        commit_key = self.storage.get_object_key_for_content(content)
        self.storage.put(commit)
        commit_actual = self.storage.get_object(commit_key)
        assert commit_actual.parent_key == "aaaa"
        assert commit_actual.tree_key == "bbbb"
        assert commit_actual.message == "cccc"

    def test_put_commit(self):
        commit = Commit("aaaa", "bbbb", message="cccc")
        content = self.storage._serialize_object_to_bytes(commit)
        print("content: {}".format(content))
        commit_key = self.storage.get_object_key_for_content(content)
        print("commit_key: {}".format(commit_key))
        commit_path = self.storage.paths.get_object_path(
            commit_key, must_exist=False
        )
        assert not commit_path.exists()
        self.storage.put(commit)
        print(commit_path)
        assert commit_path.exists()

    # @skip("Not Implemented")
    # def test_put_index(self):
    #     assert False
    #
    # @skip("Not Implemented")
    # def test_get_index(self):
    #     assert False
    #
    # @skip("Not Implemented")
    # def test_get_object_key_for_content(self):
    #     assert False
    #
    # @skip("Not Implemented")
    # def test_serialize_object_to_bytes(self):
    #     assert False
    #
    # @skip("Not Implemented")
    # def test_write_object(self):
    #     assert False
