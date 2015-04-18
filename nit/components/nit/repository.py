#! /usr/bin/env python
"""
"""
import os

from nit.core.log import getLogger
from nit.core.blob import Blob
from nit.components.nit.storage import NitStorage
from nit.components.nit.serialization import NitSerializer
from nit.core.errors import NitUserError, NitRefNotFoundError
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

    def status(self):
        try:
            head_key = self.storage.get_ref("HEAD")
        except NitRefNotFoundError as exc:
            logger.info("Initial commit")
            return
        head = self.storage.get_object(head_key)
        index = self.storage.get_index()
        diff = head.diff(index)
        logger.info(str(diff))

    def add(self, *relative_file_paths):
        blobs = []

        index = self.storage.get_index()

        if not index:
            from nit.core.index import Index
            index = Index()

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
                node = Tree.Node(relative_file_path, key)
                index.add_node(node)

        self.storage.put(index)

        return blobs

    def cat(self, key):
        obj = self.storage.get_object(key)
        return str(obj)

    def commit(self):
        index = self.storage.get_index()
        if not index:
            raise NitUserError("Nothing to commit!")
        key = self.storage.put_tree(index)
        self.storage.put_ref("HEAD", key)

    def diff(self):
        raise Exception("boo")

    def checkout(self):
        raise NotImplementedError("checkout")
