#! /usr/bin/env python
"""
"""
from datetime import datetime
from nit.core.storage import Storable


class Commit(Storable):
    """
    Stores a snapshot of the tracked files in the working
    tree at a particular time, along with metadata like
    the time of creation, the author, and a user-specified
    log message.

    The most important piece of information in a commit is
    a reference to a tree which represents the working
    directory at the time the commit was made. This tree
    can be used to reconstruct that state of the working
    directory.
    """

    def __init__(
            self,
            parent_key,
            tree_key,
            message="",
            created_timestamp=None,
            author=None
    ):
        self.tree_key = tree_key
        self.parent_key = parent_key
        self.message = message
        self.created_timestamp = created_timestamp or datetime.now()
        self.author = author or "Unknown <unknown>"

    @classmethod
    def accept_get(cls, storage, keyish):
        return storage.get_commit(cls, keyish)

    def accept_put(self, storage):
        return storage.put_commit(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_commit(cls)

    def accept_serializer(self, serializer):
        return serializer.serialize_commit(self)

    def __str__(self):
        return (
            "Created: {}\n"
            "Parent:  {}\n"
            "  Tree:  {}\n"
            "\n{}\n"
        ).format(
            self.created_timestamp,
            self.parent_key or "none",
            self.tree_key,
            self.message
        )
