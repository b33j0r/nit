"""
"""
import hashlib
import io
import os
import shutil
from nit.components.base.working_tree import BaseWorkingTree
from nit.core.config import BaseConfigBuilder

from nit.core.errors import NitUserError, NitRefNotFoundError
from nit.core.objects.index import Index
from nit.core.serialization import BaseSerializer
from nit.core.storage import Storage
from nit.core.log import getLogger


logger = getLogger(__name__)


class BaseStorage(Storage):

    """
    """

    def __init__(
        self,
        paths,
        serialization_cls=BaseSerializer,
        config_builder_cls=BaseConfigBuilder,
        working_tree_cls=BaseWorkingTree
    ):
        self.paths = paths
        self._serialization_cls = serialization_cls
        self._config_builder_cls = config_builder_cls
        self._working_tree_cls = working_tree_cls

    @property
    def exists(self):
        return self.paths.repo.exists()

    def _mkdir(self, path):
        try:
            path.mkdir()
        except FileExistsError:
            assert path.is_dir()

    def create(self, force=False):
        """
        Initialize the repository within the project directory

        :param force: Delete existing repository first, if found
        """
        new = not self.exists
        self._mkdir(self.paths.repo)
        self._mkdir(self.paths.objects)
        self._mkdir(self.paths.refs)
        self._mkdir(self.paths.refs/"heads")
        self._mkdir(self.paths.refs/"tags")
        self._mkdir(self.paths.repo/"hooks")
        self._mkdir(self.paths.repo/"info")
        with (self.paths.repo/"description").open('w') as f:
            f.write('No description')
        try:
            self.get_symbolic_ref("HEAD")
        except NitRefNotFoundError:
            self.put_symbolic_ref("HEAD", "refs/heads/master")

        logger.info(
            (
                "{} {repository_name} "
                "repository in {repository_path}"
            ).format(
                (
                    "Initialized empty"
                    if new else
                    "Reinitialized existing"
                ),
                repository_name=self.__class__.__name__.replace(
                    "Storage", ""
                ),
                repository_path=self.paths.repo
            )
        )

    def get_config(self):
        return self._config_builder_cls(self.paths)

    def get(self, keyish):
        return self.get_object(keyish)

    def put(self, obj):
        """

        :param obj:
        :return:
        """
        return obj.accept_put(self)

    def get_ref(self, ref):
        ref_path = self.paths.get_ref_path(ref)
        if not ref_path.exists():
            raise NitRefNotFoundError(ref_path)
        with ref_path.open('rb') as file:
            b = file.read()
            return b.decode()

    def put_ref(self, ref, key):
        relative_ref_path = self.paths.get_ref_relative_path(ref)
        ref_path = self.paths.get_ref_path(ref)
        os.makedirs(str(ref_path.parent), exist_ok=True)
        with ref_path.open('wb') as file:
            b = key.encode()
            file.write(b)
        return str(relative_ref_path)

    def get_symbolic_ref(self, name):
        ref_path = self.paths.repo/name
        if not ref_path.exists():
            raise NitRefNotFoundError(ref_path)
        with ref_path.open('rb') as file:
            b = file.read()
            symbolic_ref = b.decode()
            if symbolic_ref.startswith('ref: '):
                symbolic_ref = symbolic_ref[5:]
            return symbolic_ref

    def put_symbolic_ref(self, name, ref):
        ref_path = self.paths.repo/name
        with ref_path.open('wb') as file:
            b = ref.encode()
            file.write(b"ref: " + b)

    def get_object(self, keyish):
        file_path = self.paths.get_object_path(
            keyish, must_exist=True
        )

        with file_path.open('rb') as f:
            s = self._serialization_cls(f)
            return s.deserialize()

    def put_object(self, obj):
        content = self._serialize_object_to_bytes(obj)
        key = self.get_object_key_for_content(content)
        self._write_object(key, content)
        return key

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
            with file_path.open('wb') as f:
                f.write(content)

            logger.debug(
                logger.Fore.LIGHTGREEN_EX +
                "ADDED" +
                logger.Fore.RESET +
                "   {}".format(key)
            )

    def get_index(self):
        try:
            with open(self.paths.index_str, 'rb') as f:
                s = self._serialization_cls(f)
                return s.deserialize_index(Index)
        except FileNotFoundError:
            return None

    def put_index(self, index):
        with self.paths.index.open('wb') as file:
            s = self._serialization_cls(file)
            s.serialize_index(index, self.paths)

    def get_working_tree(self):
        return self._working_tree_cls(self)

    def put_blob(self, blob):
        return self.put_object(blob)

    def put_commit(self, commit):
        return self.put_object(commit)

    def put_tree(self, tree):
        return self.put_object(tree)

    def get_object_key_for(
        self, obj
    ):
        content = self._serialize_object_to_bytes(obj)
        return self.get_object_key_for_content(content)

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
            return memory_file.getvalue()

    def serialize_object_to_path(self, obj, path):
        assert path.is_absolute()
        b = self._serialize_object_to_bytes(obj)
        with path.open('wb') as f:
            f.write(b)
