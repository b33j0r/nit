#! /usr/bin/env python
"""
"""

from nit.core.storage import NitStorageStrategy
from nit.core.serialization import BaseSerializationStrategy


class Repository:
    """
    """
    def __init__(
        self,
        project_dir_path,
        storage_cls=NitStorageStrategy,
        staging_cls=None,
        serialization_cls=BaseSerializationStrategy
    ):
        self.storage = storage_cls(project_dir_path, serialization_cls)
        self.stage = staging_cls(self.storage)

    def init(self, force=False):
        self.storage.init(force=force)

    def add(self, relative_file_path):
        self.stage.add(relative_file_path)

    def commit(self):
        raise NotImplementedError("commit")

    def checkout(self):
        raise NotImplementedError("checkout")
