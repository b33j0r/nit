#! /usr/bin/env python
"""
"""
import os
from pathlib import Path
from nit.core.errors import NitExpectedError
from nit.core.log import getLogger
from nit.core.objects.blob import Blob
from nit.core.objects.commit import Commit
from nit.core.objects.index import Index
from nit.core.objects.tree import TreeNode, Tree

from nit.core.working_tree import WorkingTree


logger = getLogger(__name__)


class BaseWorkingTree(WorkingTree):

    """
    Creates a `Tree` from the project's working directory.
    """

    def __init__(self, storage, ignore=None):
        self.storage = storage
        self.ignore = ignore
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
            node = TreeNode(rp, key, p.stat())
        return node

    def walk(self):
        yield from os.walk(str(self.paths.project))


class BaseWorkingTreeEditor(BaseWorkingTree):

    """
    """

    def __init__(self, storage, ignore):
        super().__init__(storage, ignore=ignore)

    def merge(self, tree):
        """
        """
        raise NotImplementedError("Definitely not implemented!")

    def replace(self, tree):
        """
        """
        assert isinstance(tree, Tree)

        assert not isinstance(tree, (Commit, Index)), (
            "Should be a Tree, but is {}".format(
                tree.__class__.__name__
            )
        )

        if not self.ignore:
            raise NitExpectedError(
                "For safety, we don't allow this operation "
                "if an ignore strategy is not specified"
            )

        rm_paths = []
        cp_keys_and_paths = []

        logger.debug("Working tree:")

        for node in self:
            if self.ignore(node.path):
                continue
            logger.debug(node.path)
            assert isinstance(node.path, Path)
            rm_path = self.storage.paths.project/node.path
            assert rm_path.is_absolute()
            rm_paths.append(rm_path)

        logger.debug("---")
        logger.debug("Tree being checked out:")

        for node in tree:
            logger.debug(node.path)
            cp_path = self.storage.paths.project/node.path
            assert cp_path.is_absolute()
            self.storage.get(node.key)
            cp_keys_and_paths.append((node.key, cp_path))

        # We've been a bit more careful about planning our
        # operations; now we do the scary part

        # Delete the stuff that's here
        for rm_path in rm_paths:
            os.remove(str(rm_path))

        # Copy objects into the working dir from the db
        for key, cp_path in cp_keys_and_paths:
            obj = self.storage.get(key)
            with cp_path.open('wb') as f:
                f.write(obj.content)
