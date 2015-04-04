#! /usr/bin/env python
"""
"""
import hashlib

import os
import shutil
from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractproperty

from nit.core.errors import NitUserError
from nit.core.serialization import Serializable


class Storable(Serializable, metaclass=ABCMeta):

    """
    Something that can be stored, such as a stream or a commit
    """

    @abstractproperty
    def key(self):
        """
        The identifier used to retrieve the same object using `get`.
        """
        pass

    @abstractmethod
    def put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument.
        """
        pass

    @abstractclassmethod
    def get(cls, storage, key):
        """
        Accept method for a storage visitor retrieving an object.

        Should call the appropriate method on `storage` with
        `self` and `key` as the arguments and return the result.
        """
        pass

class StorableBlob(Storable):

    """
    """

    def __init__(self, content_bytes):
        self._content_bytes = content_bytes
        self._content_len = len(self.content)

    @property
    def key(self):
        return hashlib.sha1(self.content).hexdigest()

    def __len__(self):
        return self._content_len

    @property
    def content(self):
        return self._content_bytes

    def put(self, storage):
        storage.put_blob(self)

    @classmethod
    def get(cls, storage, key):
        storage.get_blob(cls, key)

    def accept_serializer(self, serializer):
        serializer.serialize_blob(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        deserializer.deserialize_blob(cls)


class BaseStorageStrategy:
    """
    """

    def __init__(self, project_dir_path, serialization_cls):
        if not os.path.exists(project_dir_path):
            raise NitUserError(
                "Project directory '{}' does not exist".format(
                    project_dir_path
                )
            )
        if not os.path.isdir(project_dir_path):
            raise NitUserError(
                "Project path '{}' is not a directory".format(
                    project_dir_path
                )
            )
        self._project_dir_path = project_dir_path
        self._serialization_cls = serialization_cls

    @property
    def project_dir_path(self):
        """
        The absolute path of the project directory
        """
        return self._project_dir_path

    def init(self, force=False):
        """
        Initialize the repository within the project directory

        :param force: Delete existing repository first, if found
        """
        raise NotImplementedError("init")

    def put(self, obj):
        obj.put(self)

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
        serialization_cls=None,
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

    def destroy(self, ignore_errors=True):
        shutil.rmtree(self.repo_dir_path, ignore_errors=ignore_errors)

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

    def __contains__(self, key):
        blob_dir_path, blob_file_name = self.get_object_path(key)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        if not os.path.exists(blob_file_path):
            return False
        return True

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

        if not os.path.exists(blob_file_path):
            raise NitUserError("Object '{}' is unknown".format(key))

        with open(blob_file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return obj_cls.deserialize(s)

    def put_blob(self, blob):
        self.put_object(blob)

    def get_blob(self, blob_cls, key):
        return self.get_object(blob_cls, key)
