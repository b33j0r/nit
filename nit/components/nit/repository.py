#! /usr/bin/env python
"""
"""
from functools import wraps
import os
from pathlib import Path
from nit.core.commit import Commit

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
        paths,
        storage_cls=NitStorage,
        serialization_cls=NitSerializer
    ):
        self.storage = storage_cls(
            paths,
            serialization_cls=serialization_cls
        )

    @property
    def exists(self):
        return self.storage.exists

    def create(self, force=False):
        self.storage.create(force=force)

    def destroy(self):
        self.storage.destroy()

    def status(self):
        try:
            symbolic_ref = self.storage.get_symbolic_ref("HEAD")
            head_key = self.storage.get_ref(symbolic_ref)
        except NitRefNotFoundError as exc:
            logger.info("Initial commit")
            return
        head_commit = self.storage.get_object(head_key)
        head = self.storage.get_object(head_commit.tree_key)
        index = self.storage.get_index()
        diff = head.diff(index)
        logger.info(str(diff))

    def add(self, *relative_file_paths):
        blobs = []

        index = self.storage.get_index()

        if not index:
            from nit.core.index import Index
            index = Index()

        file_paths = [
            self.storage.paths.project/Path(rfp)
            for rfp in relative_file_paths
        ]

        for file_path in file_paths:
            if not file_path.exists():
                raise NitUserError(
                    "The file '{}' does not exist".format(
                        file_path
                    )
                )
            with open(str(file_path), 'rb') as file:
                contents = file.read()
                blob = Blob(contents)
                key = self.storage.put(blob)
                relative_file_path = file_path.relative_to(
                    self.storage.paths.project
                )
                blobs.append((key, relative_file_path, blob))
                node = Tree.Node(
                    relative_file_path,
                    key
                )
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
        try:
            branch_ref = self.storage.get_symbolic_ref("HEAD")
            parent_key = self.storage.get_ref(branch_ref)
        except:
            parent_key = ""
        tree_key = self.storage.put_tree(index)
        commit_obj = Commit(parent_key, tree_key, "Message!")
        commit_key = self.storage.put(commit_obj)
        self.storage.put_ref("heads/master", commit_key)
        self.storage.put_symbolic_ref("HEAD", "heads/master")

    def diff(self):
        raise Exception("boo")

    def checkout(self):
        raise NotImplementedError("checkout")
