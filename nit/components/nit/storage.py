#! /usr/bin/env python
"""
"""
import glob
import hashlib
import io
import os
import shutil

from nit.core.log import getLogger
from nit.core.storage import Storage
from nit.core.errors import NitUserError
from nit.components.nit.serialization import NitSerializer


logger = getLogger(__name__)


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
        return "objects"

    @property
    def object_dir_path(self):
        return os.path.join(self.repo_dir_path, self.object_dir_name)

    def get_object_path(self, keyish, must_exist=False):
        if not must_exist:
            return self.object_dir_path, keyish

        if len(keyish) == 40:
            blob_file_path = os.path.join(self.object_dir_path, keyish)

            if not os.path.exists(blob_file_path):
                raise NitUserError("No object matching '{}'".format(keyish))

            key = keyish

        else:
            blob_file_path = os.path.join(self.object_dir_path, keyish + "*")

            logger.debug("Searching for an object matching '{}'".format(blob_file_path))

            search_result = glob.glob(blob_file_path)

            if len(search_result) == 0:
                raise NitUserError("No object matching '{}'".format(keyish))

            if len(search_result) > 1:
                logger.debug("Multiple objects found:\n{}".format("\n".join(
                    "    " + s for s in search_result
                )))
                raise NitUserError("Multiple objects matching '{}'".format(keyish))

            key = os.path.basename(search_result[0])

        return self.object_dir_path, key

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
        logger.debug(("Destroying {repository_name} "
                      "repository in {repository_path}").format(
            repository_name=self.__class__.__name__.replace("Storage", ""),
            repository_path=self.repo_dir_path
        ))
        shutil.rmtree(self.repo_dir_path, ignore_errors=ignore_errors)

    def put(self, obj):
        obj.accept_put(self)

    def get(self, key):
        return self.get_blob(key)

    def __contains__(self, key):
        blob_dir_path, blob_file_name = self.get_object_path(key, must_exist=True)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        if not os.path.exists(blob_file_path):
            return False
        return True

    def put_blob(self, blob):
        with io.BytesIO() as memory_file:
            s = self._serialization_cls(memory_file)
            s.serialize(blob)

            memory_file.seek(0)
            content = memory_file.read()

        key = hashlib.sha1(content).hexdigest()

        obj_dir_path, obj_file_path = self.get_object_path(key, must_exist=False)
        blob_file_path = os.path.join(obj_dir_path, obj_file_path)

        os.makedirs(obj_dir_path, exist_ok=True)

        if os.path.exists(blob_file_path):
            logger.debug(
                logger.Fore.LIGHTBLACK_EX +
                "EXISTS" +
                logger.Fore.RESET +
                "  {}".format(key)
            )
        else:
            with open(blob_file_path, 'wb') as f:
                f.write(content)

            logger.debug(
                logger.Fore.LIGHTGREEN_EX +
                "ADDED" +
                logger.Fore.RESET +
                "   {}".format(key)
            )

    def get_blob(self, keyish):
        blob_dir_path, blob_file_name = self.get_object_path(keyish, must_exist=True)
        blob_file_path = os.path.join(blob_dir_path, blob_file_name)

        with open(blob_file_path, 'rb') as f:
            s = self._serialization_cls(f)
            return s.deserialize()

    def put_tree(self, tree):
        self.put_blob(tree)
