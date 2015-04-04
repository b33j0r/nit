#! /usr/bin/env python
"""
"""
import os
import hashlib
import shutil
from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractproperty

from nit.core.errors import NitUserError
from nit.core.serialization import Serializable, NitSerializer


class Storable(Serializable, metaclass=ABCMeta):

    """
    Something that can be stored, such as a file or a commit
    """

    @abstractproperty
    def key(self):
        """
        The identifier used to retrieve the same object using `get`.
        """
        pass

    @abstractmethod
    def accept_put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument.
        """
        pass

    @abstractclassmethod
    def accept_get(cls, storage, key):
        """
        Accept method for a storage visitor retrieving an object.

        Should call the appropriate method on `storage` with
        `self` and `key` as the arguments and return the result.
        """
        pass

    @abstractmethod
    def accept_serializer(self, serializer):
        pass

    @abstractmethod
    def accept_deserializer(cls, deserializer):
        pass


class NitBlob(Storable):

    """
    """

    def __init__(self, content_bytes):
        self._content_bytes = content_bytes
        self._content_len = len(self.content)

    @property
    def content(self):
        return self._content_bytes

    def __len__(self):
        return self._content_len

    @property
    def key(self):
        sha1 = hashlib.sha1(self.content).hexdigest()
        return sha1

    def accept_put(self, storage):
        storage.put_blob(self)

    @classmethod
    def accept_get(cls, storage, key):
        storage.get_blob(cls, key)

    def accept_serializer(self, serializer):
        serializer.serialize_blob(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        deserializer.deserialize_blob(cls)


class Storage(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def create(self, force=False):
        pass

    @abstractmethod
    def destroy(self, ignore_errors=True):
        pass

    @abstractmethod
    def put(self, storable):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put_blob(self, blob):
        pass

    @abstractmethod
    def get_blob(self, key):
        pass


class NitStorage(Storage):
    """
    """

    def __init__(
        self,
        project_dir_path,
        serialization_cls=NitSerializer,
        repo_dir_name=".nit"
    ):
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

        self._repo_dir_name = repo_dir_name
        self._project_dir_path = project_dir_path
        self._serialization_cls = serialization_cls

    def create(self, force=False):
        """
        Initialize the repository within the project directory

        :param force: Delete existing repository first, if found
        """
        self._create_verify_repo_dir(force)
        self._create_dir_structure()

    def _create_dir_structure(self):
        os.makedirs(self.repo_dir_path)
        os.makedirs(self.object_dir_path, exist_ok=True)

    def _create_verify_repo_dir(self, force):
        if os.path.exists(self.repo_dir_path):
            if force:
                self.destroy()
            else:
                raise NitUserError(
                    "'{}' already exists!".format(self.repo_dir_path)
                )

    def destroy(self, ignore_errors=True):
        shutil.rmtree(self.repo_dir_path, ignore_errors=ignore_errors)

    def put(self, obj):
        obj.accept_put(self)

    def get(self, key):
        return self.get_blob(key)

    def put_blob(self, blob):
        obj_dir_path, obj_file_path = self.get_object_path(blob.key)
        os.makedirs(obj_dir_path, exist_ok=True)
        blob_file_path = os.path.join(obj_dir_path, obj_file_path)

        with open(blob_file_path, 'wb') as f:
            s = self._serialization_cls(f)
            s.serialize(blob)

    def get_blob(self, key):
        blob_dir_path, blob_file_name = self.get_object_path(key)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        if not os.path.exists(blob_file_path):
            raise NitUserError("Object '{}' is unknown".format(key))

        with open(blob_file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return s.deserialize()

    @property
    def project_dir_path(self):
        """
        The absolute path of the project directory
        """
        return self._project_dir_path

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

    def __contains__(self, key):
        blob_dir_path, blob_file_name = self.get_object_path(key)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        if not os.path.exists(blob_file_path):
            return False
        return True
