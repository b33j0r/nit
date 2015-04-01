#! /usr/bin/env python
"""
"""
import os
import shutil
from nit.core.errors import NitUserError
from nit.core.serialization import BaseSerializationStrategy


class BaseStorageStrategy:
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


class NitStorageStrategy(BaseStorageStrategy):

    """
    """

    def __init__(
        self,
        project_dir_path,
        serialization_cls=BaseSerializationStrategy,
        repo_dir_name=".nit"
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
    def object_dir_name(self):
        return "objects"

    @property
    def object_dir_path(self):
        return os.path.join(self.repo_dir_path, self.object_dir_name)

    def get_object_path(self, key):
        return self.object_dir_path, key

    def init(self, force=False):
        self._init_verify_repo_dir(force)
        self._init_dir_structure()

    def destroy(self):
        shutil.rmtree(self.repo_dir_path, ignore_errors=True)

    def _init_dir_structure(self):
        os.makedirs(self.repo_dir_path)
        os.makedirs(self.object_dir_path, exist_ok=True)

    def _init_verify_repo_dir(self, force):
        if os.path.exists(self.repo_dir_path):
            if force:
                self.destroy()
            else:
                raise NitUserError(
                    "'{}' already exists!".format(self.repo_dir_path)
                )

    def put_object(self, obj):
        obj_dir_path, obj_file_path = self.get_object_path(obj.key)
        os.makedirs(obj_dir_path, exist_ok=True)
        blob_file_path = os.path.join(obj_dir_path, obj_file_path)

        with open(blob_file_path, 'wb') as f:
            s = self._serialization_cls(f)
            obj.serialize(s)

    def get_object(self, obj_cls, key):
        blob_dir_path, blob_file_name = self.get_object_path(key)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        with open(blob_file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return obj_cls.deserialize(s)

    def put_blob(self, blob):
        self.put_object(blob)

    def get_blob(self, blob_cls, key):
        return self.get_object(blob_cls, key)
