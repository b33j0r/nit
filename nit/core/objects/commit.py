#! /usr/bin/env python
"""
"""
from datetime import datetime
from nit.core.storage import Storable


class Commit(Storable):
    """
    """

    def __init__(self, parent_key, tree_key, message="", created_timestamp=None):
        self.tree_key = tree_key
        self.parent_key = parent_key
        self.message = message
        self.created_timestamp = created_timestamp or datetime.now()

    def accept_put(self, storage):
        return storage.put_commit(self)

    def accept_serializer(self, serializer):
        return serializer.serialize_commit(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_commit(cls)

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
