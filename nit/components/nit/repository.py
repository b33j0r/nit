#! /usr/bin/env python
"""
"""
import os
from pathlib import Path
import textwrap
from nit.core.diff import TreeDiffFormatter

from nit.core.log import getLogger
from nit.core.errors import NitUserError, NitRefNotFoundError
from nit.core.repository import Repository
from nit.core.commit import Commit
from nit.core.blob import Blob
from nit.core.status import BaseStatusStrategy
from nit.core.tree import Tree, TreeNode
from nit.components.nit.ignore import NitIgnoreStrategy
from nit.components.nit.storage import NitStorage
from nit.components.nit.serialization import NitSerializer


logger = getLogger(__name__)


class NitRepository(Repository):
    """
    """
    def __init__(
        self,
        paths,
        storage_cls=NitStorage,
        serialization_cls=NitSerializer,
        ignore_cls = NitIgnoreStrategy
    ):
        self.storage = storage_cls(
            paths,
            serialization_cls=serialization_cls
        )
        self.ignore = ignore_cls(
            paths
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
            head_commit = self.storage.get_object(head_key)
            head = self.storage.get_object(head_commit.tree_key)
        except NitRefNotFoundError as exc:
            logger.info("Initial commit")
            # return
            head = Tree()
        index = self.storage.get_index()

        stage = Tree()
        walk = os.walk(str(self.storage.paths.project))
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                p = Path(os.path.join(dirpath, filename))
                if p.is_file() and p.exists():
                    p.resolve()
                    rp = p.relative_to(self.storage.paths.project)
                    with open(str(p), 'rb') as file:
                        contents = file.read()
                        blob = Blob(contents)
                        key = self.storage.get_object_key_for(blob)
                        stage.add_node(TreeNode(rp, key))

        diff = BaseStatusStrategy(
            head, index, stage, ignorer=self.ignore.ignore
        )
        fmt = TreeDiffFormatter()
        logger.info(fmt.format(diff))

    def add(self, *relative_file_paths, force=False):
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
            if not force and self.ignore.ignore(file_path):
                logger.warn(
                    (
                        "The file '{}' is ignored "
                        "(use --force to override)"
                    ).format(
                        file_path
                    )
                )
                continue
            with open(str(file_path), 'rb') as file:
                contents = file.read()
                blob = Blob(contents)
                key = self.storage.put(blob)
                relative_file_path = file_path.relative_to(
                    self.storage.paths.project
                )
                blobs.append(
                    (key, relative_file_path, blob)
                )
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

    def log(self, key=None):
        if not key:
            key = self._get_head_commit_key()
        try:
            commit = self.storage.get_object(key)
        except IsADirectoryError:
            commit = None

        def indent(lines, amount, ch=' '):
            lines = textwrap.fill(lines)
            padding = amount * ch
            return padding + ('\n'+padding).join(lines.split('\n'))

        if commit:
            logger.info(
                (
                    logger.Fore.YELLOW +
                    "commit {key}\n" +
                    logger.Fore.RESET +
                    "Date:  {created_timestamp}\n"
                    "\n"
                    "{message}\n"
                ).format(
                    key=key,
                    created_timestamp=commit.created_timestamp,
                    message=indent(commit.message, 4)
                )
            )
            if commit.parent_key:
                return [commit] + self.log(
                    key=commit.parent_key
                )
        return []

    def commit(self):
        index = self.storage.get_index()
        if not index:
            raise NitUserError("Nothing to commit!")
        parent_key = self._get_head_commit_key()
        tree_key = self.storage.put_tree(index)
        commit_obj = Commit(parent_key, tree_key,
                            message="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris tincidunt tempor justo eget tempor.
Aliquam vestibulum id erat sit amet vestibulum. Vivamus pulvinar tortor nisl, a mollis neque vulputate ut. Quisque massa neque, euismod eget elit sed, porttitor eleifend nisi. Praesent facilisis urna et tincidunt fermentum. Vestibulum rutrum nibh gravida, malesuada nisi quis, vulputate mauris. Mauris vel quam sit amet sapien ornare facilisis vel ut lacus. Maecenas sollicitudin tincidunt magna, vitae tincidunt turpis. Sed elementum auctor odio id ultricies. Proin non lorem ex. Suspendisse potenti. Maecenas ultricies, ex ut pharetra sagittis, erat lectus pretium nibh, vitae venenatis ipsum lacus vitae urna. Curabitur non tortor non lectus finibus tempor. Suspendisse potenti. Nullam feugiat, nibh eget sagittis tristique, dui mi elementum ante, eu condimentum massa ipsum et neque."""
                            )
        commit_key = self.storage.put(commit_obj)
        self.storage.put_ref("heads/master", commit_key)
        self.storage.put_symbolic_ref("HEAD", "heads/master")

    def _get_head_commit_key(self):
        try:
            branch_ref = self.storage.get_symbolic_ref("HEAD")
            head_key = self.storage.get_ref(branch_ref)
        except:
            head_key = ""
        return head_key

    def diff(self):
        raise Exception("boo")

    def checkout(self):
        raise NotImplementedError("checkout")
