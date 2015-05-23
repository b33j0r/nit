#! /usr/bin/env python
"""
"""
import os
from pathlib import Path
from nit.core.objects.blob import Blob
from nit.core.objects.tree import TreeNode

from nit.core.working_tree import WorkingTree


class BaseWorkingTree(WorkingTree):

    """
    Creates a `Tree` from the project's working directory.
    """

    def __init__(self, storage):
        self.storage = storage
        self.paths = self.storage.paths

        super().__init__(nodes=[])

        for base, dir_names, file_names in self.walk():
            self._walk_files(base, file_names)

    def _walk_files(self, base, file_names):
        for filename in file_names:
            self._walk_file(base, filename)

    def _exclude_path(self, p):
        return not (p.is_file() and p.exists())

    def _walk_file(self, base, filename):
        p = Path(os.path.join(base, filename))
        p.resolve()
        if self._exclude_path(p):
            return
        node = self._read_tree_node(p)
        self.add_node(node)

    def _read_tree_node(self, p):
        rp = p.relative_to(self.paths.project)
        with p.open('rb') as file:
            contents = file.read()
            blob = Blob(contents)
            key = self.storage.get_object_key_for(blob)
            node = TreeNode(rp, key)
        return node

    def walk(self):
        yield from os.walk(str(self.paths.project))
