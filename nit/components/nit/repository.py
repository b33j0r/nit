#! /usr/bin/env python
"""
"""
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
from io import BytesIO
from nit.components.git.status import GitStatusFormatter
from nit.components.nit.status import NitStatusFormatter

from nit.core.log import getLogger
from nit.core.errors import NitUserError, NitRefNotFoundError
from nit.core.repository import Repository
from nit.core.objects.commit import Commit
from nit.core.objects.blob import Blob
from nit.core.objects.tree import Tree
from nit.core.status import BaseStatusStrategy
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
        ignore_cls=NitIgnoreStrategy,
        status_cls=BaseStatusStrategy,
        status_format_cls=GitStatusFormatter
    ):
        self.storage = storage_cls(
            paths,
            serialization_cls=serialization_cls
        )
        self.ignore = ignore_cls(
            paths
        )
        self._status_cls = status_cls
        self._status_format_cls = status_format_cls

    @property
    def exists(self):
        return self.storage.exists

    def create(self, force=False):
        self.storage.create(force=force)

    def destroy(self):
        self.storage.destroy()

    def status(self):
        status = self._status_cls.from_repo(
            self, ignorer=self.ignore.ignore
        )
        status_fmt = self._status_format_cls(status)
        logger.info(status_fmt)
        return str(status_fmt)

    def config(self, set_value=None, use_global=False):
        config = self.storage.get_config()

        if use_global:
            config = config.global_config
        else:
            config = config.repo_config

        if not 0 <= len(set_value) <= 2:
            raise NitUserError("config accepts 0-2 arguments")

        if len(set_value) == 0:
            logger.info(config)
            return config

        try:
            key, value = set_value
            config[key] = value
            config.save()
            logger.info(value)
        except ValueError:
            key = set_value[0]
            value = config.get(key)
            if value:
                logger.info(value)
            return value

    def add(self, *relative_file_paths, force=False):
        blobs = []

        index = self.storage.get_index()

        if not index:
            from nit.core.objects.index import Index
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
            with file_path.open('rb') as file:
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

    def _reformat_message(self, text, indent=4, ch=' '):
        text = text.strip()

        lines = text.split("\n")
        lines = "\n".join(textwrap.fill(line)
                          for line in lines)

        padding = indent * ch
        return padding + ('\n'+padding).join(
            lines.split('\n')
        )

    def cat(self, key):
        obj = self.storage.get_object(key)
        return str(obj)

    def _format_commit(self, key, commit):
        message = self._reformat_message(
            commit.message
        )
        return (
            logger.Fore.YELLOW +
            "commit {key}\n" +
            logger.Fore.RESET +
            "Author:  {author}\n"
            "Date:    {created_timestamp}\n"
            "Tree:    {tree_key}\n"
            # "Parent:  {parent_key}\n"
            "\n"
            "{message}\n"
        ).format(
            key=key,
            author=commit.author,
            created_timestamp=commit.created_timestamp,
            tree_key=commit.tree_key,
            parent_key=commit.parent_key or "(none)",
            message=message
        )

    def log(self, key=None):
        if not key:
            key = self._get_head_commit_key()
        try:
            commit = self.storage.get_object(key)
        except IsADirectoryError:
            commit = None

        if commit:
            logger.info(
                self._format_commit(key, commit)
            )
            if commit.parent_key:
                return [commit] + self.log(
                    key=commit.parent_key
                )
        return []

    def commit(self, message=""):
        config = self.storage.get_config()
        author_str = "{} <{}>".format(
            config["user.name"],
            config["user.email"]
        )
        index = self.storage.get_index()
        if not index:
            raise NitUserError("Nothing to commit!")
        parent_key = self._get_head_commit_key()
        parent_commit = self.storage.get_object(parent_key)
        tree_key = self.storage.put_tree(index)
        if parent_commit and tree_key == parent_commit.tree_key:
            raise NitUserError("The tree to be committed "
                               "is identical to the parent.")
        if not message:
            message = self._get_commit_message_with_editor()
        if not message:
            raise NitUserError("No commit message specified!")

        commit_obj = Commit(
            parent_key,
            tree_key,
            message=message,
            author=author_str
        )

        commit_key = self.storage.put(commit_obj)
        self.storage.put_ref("heads/master", commit_key)
        self.storage.put_symbolic_ref("HEAD", "heads/master")

    def _get_editor_command(self, temp_file_path):
        editor = os.environ.get("EDITOR", "vi")
        return [editor, temp_file_path]

    def _get_commit_message_with_editor(self):
        temp_file_path = tempfile.mktemp(
            prefix="commit-message-"
        )
        editor_cmd = self._get_editor_command(temp_file_path)
        if subprocess.check_call(editor_cmd):
            return None
        if not os.path.exists(temp_file_path):
            return None
        with open(temp_file_path, 'r', encoding='utf-8') as tf:
            message = tf.read()
            message = message.strip()
            return message

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
