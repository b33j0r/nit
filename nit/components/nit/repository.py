#! /usr/bin/env python
"""
"""
import os

from nit.core.log import getLogger
from nit.core.blob import Blob
from nit.components.nit.storage import NitStorage
from nit.components.nit.serialization import NitSerializer
from nit.core.errors import NitUserError
from nit.core.repository import Repository
from nit.core.tree import Tree


logger = getLogger(__name__)


class NitRepository(Repository):
    """
    """
    def __init__(
        self,
        project_dir_path,
        storage_cls=NitStorage,
        serialization_cls=NitSerializer
    ):
        self.storage = storage_cls(
            project_dir_path,
            serialization_cls=serialization_cls
        )

    def create(self, force=False):
        self.storage.create(force=force)

    def destroy(self):
        self.storage.destroy()

    def add(self, *relative_file_paths):
        blobs = []
        for relative_file_path in relative_file_paths:
            abs_file_path = os.path.join(
                self.storage.project_dir_path, relative_file_path
            )
            if not os.path.exists(abs_file_path):
                raise NitUserError(
                    "The file '{}' does not exist".format(
                        abs_file_path
                    )
                )
            with open(abs_file_path, 'rb') as file:
                contents = file.read()
                blob = Blob(contents)
                key = self.storage.put(blob)
                blobs.append((key, relative_file_path, blob))
        return blobs

    def cat(self, key):
        obj = self.storage.get(key)
        return str(obj)

    def commit(self):
        abs_file_path = os.path.join(
            self.storage.project_dir_path, "a"
        )

        with open(abs_file_path, 'wb') as file:
            file.write(b"a1")

        obj = Tree()
        for key, relative_file_path, blob in self.add("a"):
            obj.add_node(Tree.Node(relative_file_path, key))
        self.storage.put(obj)

        with open(abs_file_path, 'wb') as file:
            file.write(b"a2")

        obj2 = Tree()
        for key, relative_file_path, blob in self.add("a", "b"):
            obj2.add_node(Tree.Node(relative_file_path, key))
        self.storage.put(obj2)

        obj3 = Tree()
        for key, relative_file_path, blob in self.add("c"):
            obj3.add_node(Tree.Node(relative_file_path, key))
        self.storage.put(obj3)

    def diff(self):
        obj = self.storage.get_object("064c1aac7752cd50c187752a50e5111e91b80a54")

        obj2 = self.storage.get_object("f51eeed6772a0643a255333e6fb2e624dd667052")
        diff = obj.diff(obj2)
        logger.info("{}".format(diff))

        obj3 = self.storage.get_object("2be8eba8ab1379641d81c4f32945d99a041450b5")
        diff = obj.diff(obj3)
        logger.info("{}".format(diff))

    def checkout(self):
        raise NotImplementedError("checkout")
