#! /usr/bin/env python
"""
"""
from abc import (
    ABCMeta,
    abstractmethod,
    abstractclassmethod
)
import io
import os
import glob
import hashlib
import shutil

from nit.core.log import getLogger
from nit.core.serialization import Serializable, BaseSerializer
from nit.core.errors import NitUserError


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

    @abstractmethod
    def create(self, force=False):
        pass

    @abstractmethod
    def destroy(self, ignore_errors=True):
        pass

    @abstractmethod
    def put(self, storable):
        """
        Inserts a `Storable` into the Storage.

        :param storable (Storable): The object to insert
        """
        pass

    @abstractmethod
    def get(self, key):
        """
        Returns an instance of `Storable` having the given `key`

        :param key:
        :return (Storable):
        """
        pass

    @abstractmethod
    def put_blob(self, blob):
        pass

    @abstractmethod
    def put_tree(self, tree):
        pass


class BaseStorage(Storage):

    """
    """

    def __init__(
        self,
        project_dir_path,
        serialization_cls=BaseSerializer,
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

    @property
    def project_dir_path(self):
        """
        The absolute path of the project directory
        """
        return self._project_dir_path

    @property
    def repo_dir_name(self):
        """
        The name of the repository directory (e.g. '.nit' or '.git')
        """
        return self._repo_dir_name

    @property
    def repo_dir_path(self):
        """
        The absolute path of the repository directory (e.g. '~/project/.nit')
        """
        return os.path.join(self.project_dir_path, self.repo_dir_name)

    @property
    def object_dir_name(self):
        """

        """
        return "objects"

    @property
    def object_dir_path(self):
        """
        The absolute path of the object directory within the repository
        """
        return os.path.join(self.repo_dir_path, self.object_dir_name)

    @property
    def index_name(self):
        """

        """
        return "index"

    @property
    def index_path(self):
        """
        The absolute path of the index within the repository
        """
        return os.path.join(self.repo_dir_path, self.index_name)

    def destroy(self, ignore_errors=True):
        """

        :param ignore_errors:
        :return:
        """
        logger.debug(
            ("Destroying {repository_name} "
             "repository in {repository_path}").format(
                repository_name=self.__class__.__name__.replace("Storage", ""),
                repository_path=self.repo_dir_path
            )
        )
        shutil.rmtree(self.repo_dir_path, ignore_errors=ignore_errors)

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
            repository_path=self.repo_dir_path
        ))

    def _create_verify_repo_dir(self, force):
        if os.path.exists(self.repo_dir_path):
            if force:
                self.destroy()
            else:
                raise NitUserError(
                    "'{}' already exists!".format(self.repo_dir_path)
                )

    def _create_dir_structure(self):
        os.makedirs(self.repo_dir_path)
        os.makedirs(self.object_dir_path, exist_ok=True)

    def put(self, obj):
        """

        :param obj:
        :return:
        """
        return obj.accept_put(self)

    def get(self, key):
        """

        :param key:
        :return:
        """
        return self.get_object(key)

    def put_index(self, index):
        with open(self.index_path, 'wb') as file:
            s = self._serialization_cls(file)
            s.serialize(index)

    def get_index(self):
        try:
            with open(self.index_path, 'rb') as f:
                s = self._serialization_cls(f)
                return s.deserialize()
        except FileNotFoundError:
            return None

    def put_blob(self, blob):
        return self.put_object(blob)

    def put_tree(self, tree):
        return self.put_object(tree)

    def put_object(self, obj):
        content = self._serialize_object_to_bytes(obj)
        key = self.get_object_key_for_content(content)
        self._write_object(key, content)
        return key

    def get_object(self, keyish):
        dir_path, file_name = self.get_object_path(keyish, must_exist=True)
        file_path = os.path.join(dir_path, file_name)

        with open(file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return s.deserialize()

    def get_object_key_for_content(self, content):
        """
        :param content:
        :return:
        """
        return hashlib.sha1(content).hexdigest()

    def get_object_path(self, keyish, must_exist=False):
        """

        :param keyish:
        :param must_exist:
        :return:
        """
        if not must_exist:
            return self.object_dir_path, keyish

        if len(keyish) == 40:
            blob_file_path = os.path.join(self.object_dir_path, keyish)
            if not os.path.exists(blob_file_path):
                raise NitUserError("No object matching '{}'".format(keyish))
            key = keyish
        else:
            blob_file_path = os.path.join(self.object_dir_path, keyish + "*")
            logger.debug(
                "Searching for an object matching '{}'".format(
                    blob_file_path
                )
            )
            search_result = glob.glob(blob_file_path)
            if len(search_result) == 0:
                raise NitUserError(
                    "No object matching '{}'".format(keyish)
                )
            if len(search_result) > 1:
                logger.debug(
                    "Multiple objects found:\n{}".format(
                        "\n".join("    " + s for s in search_result)
                    )
                )
                raise NitUserError(
                    "Multiple objects matching '{}'".format(keyish)
                )
            key = os.path.basename(search_result[0])

        return self.object_dir_path, key

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

    def _write_object(self, key, content):
        """

        :param key:
        :param content:
        :return:
        """
        dir_path, file_name = self.get_object_path(key, must_exist=False)
        file_path = os.path.join(dir_path, file_name)

        os.makedirs(dir_path, exist_ok=True)

        if os.path.exists(file_path):
            logger.debug(
                logger.Fore.LIGHTBLACK_EX +
                "EXISTS" +
                logger.Fore.RESET +
                "  {}".format(key)
            )
        else:
            with open(file_path, 'wb') as f:
                f.write(content)

            logger.debug(
                logger.Fore.LIGHTGREEN_EX +
                "ADDED" +
                logger.Fore.RESET +
                "   {}".format(key)
            )
