#! /usr/bin/env python
"""
"""
import os
import shutil
from nit.core.serialization import BaseSerializationStrategy


class StorageStrategy:
    """
    """

    def __init__(self, project_dir_path, serialization_cls):
        assert os.path.exists(project_dir_path)
        assert os.path.isdir(project_dir_path)

        self._project_dir_path = project_dir_path
        self._serialization_cls = serialization_cls

    @property
    def project_dir_path(self):
        return self._project_dir_path

    def init(self, force=False):
        raise NotImplementedError("init")

    def put(self, object_):
        object_.put(self)

    def put_blob(self, blob):
        raise NotImplementedError("put_blob")

    def get_blob(self, blob_cls, key):
        raise NotImplementedError("get_blob")


class NitStorageStrategy(StorageStrategy):
    """
    """

    def __init__(
        self,
        project_dir_path,
        repo_dir_name=".nit",
        serialization_cls=BaseSerializationStrategy
    ):
        super().__init__(project_dir_path, serialization_cls)
        self._repo_dir_name = repo_dir_name

    @property
    def repo_dir_name(self):
        return self._repo_dir_name

    @property
    def repo_dir_path(self):
        return os.path.join(self.project_dir_path, self.repo_dir_name)

    @property
    def blob_dir_name(self):
        return "blobs"

    @property
    def blob_dir_path(self):
        return os.path.join(self.repo_dir_path, self.blob_dir_name)

    def init(self, force=False):
        if os.path.exists(self.repo_dir_path):
            if force:
                shutil.rmtree(self.repo_dir_path)
            else:
                # TODO: needs specific exceptions
                raise Exception("'{}' already exists!".format(self.repo_dir_path))
        os.makedirs(self.repo_dir_path)
        os.makedirs(self.blob_dir_path, exist_ok=True)

    def put_blob(self, blob):
        blob_file_path = os.path.join(self.blob_dir_path, blob.key)
        with open(blob_file_path, 'wb') as f:
            f.write(blob.content)

    def get_blob(self, blob_cls, key):
        blob_file_path = os.path.join(self.blob_dir_path, key)
        with open(blob_file_path, 'rb') as f:
            content = f.read()
            return blob_cls(content)
