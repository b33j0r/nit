#! /usr/bin/env python
"""
"""
from abc import (
    ABCMeta,
    abstractmethod,
    abstractclassmethod,
    abstractproperty)
import io
import os
import glob
import hashlib
import shutil
from pathlib import Path

from nit.core.log import getLogger
from nit.core.serialization import Serializable, BaseSerializer
from nit.core.errors import NitUserError, NitRefNotFoundError


logger = getLogger(__name__)


class Storable(Serializable, metaclass=ABCMeta):

    """
    Something that can be stored, such as a file or a commit.
    """

    @abstractmethod
    def accept_put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument.
        """
        pass


class Storage(metaclass=ABCMeta):

    """
    """

    @abstractproperty
    def exists(self):
        pass

    @abstractmethod
    def create(self, force=False):
        pass

    @abstractmethod
    def destroy(self, ignore_errors=True):
        pass

    @abstractmethod
    def put(self, storable):
        """
        Writes a `Storable` to the Storage.

        :param storable (Storable): The object to insert
        """
        pass

    @abstractmethod
    def get_ref(self, ref):
        pass

    @abstractmethod
    def put_ref(self, ref, key):
        pass

    @abstractmethod
    def get_treeish(self, treeish):
        pass

    @abstractmethod
    def get_object(self, keyish):
        """
        Returns an instance of `Storable` having the given `key`

        :param key:
        :return (Storable):
        """
        pass

    @abstractmethod
    def get_index(self):
        """
        Returns the index

        :return (Index):
        """
        pass


class BaseStorage(Storage):

    """
    """

    def __init__(
        self,
        paths_strategy,
        serialization_cls=BaseSerializer,
        repo_dir_name=".nit"
    ):
        self.paths = paths_strategy
        self._serialization_cls = serialization_cls

    @property
    def exists(self):
        return self.paths.repo.exists()

    def destroy(self, ignore_errors=True):
        """

        :param ignore_errors:
        :return:
        """
        logger.debug(
            ("Destroying {repository_name} "
             "repository in {repository_path}").format(
                repository_name=self.__class__.__name__.replace(
                    "Storage", ""
                ),
                repository_path=self.paths.repo
            )
        )
        shutil.rmtree(self.paths.repo_str, ignore_errors=ignore_errors)

    def create(self, force=False):
        """
        Initialize the repository within the project directory

        :param force: Delete existing repository first, if found
        """
        self._create_verify_repo_dir(force)
        self._create_dir_structure()
        logger.info(("Initialized empty {repository_name} "
                     "repository in {repository_path}").format(
            repository_name=self.__class__.__name__.replace("Storage", ""),
            repository_path=self.paths.repo
        ))

    def _create_verify_repo_dir(self, force):
        if not self.exists:
            return
        if force:
            self.destroy()
        else:
            raise NitUserError(
                "'{}' already exists!".format(self.paths.repo)
            )

    def _create_dir_structure(self):
        self.paths.repo.mkdir()
        self.paths.refs.mkdir()
        self.paths.objects.mkdir()

    def put(self, obj):
        """

        :param obj:
        :return:
        """
        return obj.accept_put(self)

    def put_object(self, obj):
        content = self._serialize_object_to_bytes(obj)
        key = self.get_object_key_for_content(content)
        self._write_object(key, content)
        return key

    def get_object(self, keyish):
        file_path = self.paths.get_object_path(
            keyish, must_exist=True
        )
        file_path = str(file_path)

        with open(file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return s.deserialize()

    def _write_object(self, key, content):
        """

        :param key:
        :param content:
        :return:
        """
        file_path = self.paths.get_object_path(
            key, must_exist=False
        )

        dir_path = file_path.parent

        try:
            dir_path.mkdir()
        except FileExistsError:
            pass

        if file_path.exists():
            logger.debug(
                logger.Fore.LIGHTBLACK_EX +
                "EXISTS" +
                logger.Fore.RESET +
                "  {}".format(key)
            )
        else:
            with open(str(file_path), 'wb') as f:
                f.write(content)

            logger.debug(
                logger.Fore.LIGHTGREEN_EX +
                "ADDED" +
                logger.Fore.RESET +
                "   {}".format(key)
            )

    def get_treeish(self, treeish):
        return self.get_object(treeish)

    def put_symbolic_ref(self, name, ref):
        ref_path = self.paths.repo/name
        with open(str(ref_path), 'wb') as file:
            b = ref.encode()
            file.write(b)

    def get_symbolic_ref(self, name):
        ref_path = self.paths.repo/name
        if not ref_path.exists():
            raise NitRefNotFoundError(ref_path)
        with open(str(ref_path), 'rb') as file:
            b = file.read()
            symbolic_ref = b.decode()
            return symbolic_ref

    def put_ref(self, ref, key):
        ref_path = self.paths.get_ref_path(ref)
        os.makedirs(str(ref_path.parent), exist_ok=True)
        with open(str(ref_path), 'wb') as file:
            b = key.encode()
            file.write(b)

    def get_ref(self, ref):
        ref_path = self.paths.get_ref_path(ref)
        if not ref_path.exists():
            raise NitRefNotFoundError(ref_path)
        with open(str(ref_path), 'rb') as file:
            b = file.read()
            return b.decode()

    def put_index(self, index):
        with open(self.paths.index_str, 'wb') as file:
            s = self._serialization_cls(file)
            s.serialize(index)

    def get_index(self):
        try:
            with open(self.paths.index_str, 'rb') as f:
                s = self._serialization_cls(f)
                return s.deserialize()
        except FileNotFoundError:
            return None

    def put_blob(self, blob):
        return self.put_object(blob)

    def put_commit(self, commit):
        return self.put_object(commit)

    def put_tree(self, tree):
        return self.put_object(tree)

    def get_object_key_for_content(self, content):
        """
        :param content:
        :return:
        """
        return hashlib.sha1(content).hexdigest()

    def _serialize_object_to_bytes(self, obj):
        """

        :param obj:
        :return:
        """
        with io.BytesIO() as memory_file:
            s = self._serialization_cls(memory_file)
            s.serialize(obj)

            memory_file.seek(0)
            content = memory_file.read()
        return content
