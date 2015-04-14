#! /usr/bin/env python
"""
"""
import os

from nit.components.nit.blob import NitBlob
from nit.components.nit.storage import NitStorage
from nit.components.nit.serialization import NitSerializer
from nit.core.errors import NitUserError
from nit.core.repository import Repository
from nit.core.tree import Tree, TreeNode


class NitRepository(Repository):
    """
    """
    def __init__(
        self,
        project_dir_path,
        storage_cls=NitStorage,
        staging_cls=None,
        serialization_cls=NitSerializer
    ):
        self.storage = storage_cls(project_dir_path, serialization_cls)
        # self.stage = staging_cls(self.storage)

    def create(self, force=False):
        self.storage.create(force=force)

    def destroy(self):
        self.storage.destroy()

    def add(self, *relative_file_paths):
        for relative_file_path in relative_file_paths:
            abs_file_path = os.path.join(self.storage.project_dir_path, relative_file_path)
            if not os.path.exists(abs_file_path):
                raise NitUserError("The file '{}' does not exist".format(abs_file_path))
            with open(abs_file_path, 'rb') as file:
                contents = file.read()
                blob = NitBlob(contents)
                self.storage.put(blob)



    def cat(self, key):
        obj = self.storage.get(key)
        return str(obj)

    def commit(self):
        obj = Tree()
        obj.add_node(TreeNode("jokes.txt", "5"))
        obj.add_node(TreeNode("jokes2.txt", "52"))
        self.storage.put(obj)

    def checkout(self):
        raise NotImplementedError("checkout")
