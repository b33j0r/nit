#! /usr/bin/env python
"""
"""
import hashlib

from nit.core.storage import Storable


class NitBlob(Storable):

    """
    """

    def __init__(self, content_bytes):
        self._content_bytes = content_bytes

    @property
    def content(self):
        return self._content_bytes

    def __len__(self):
        return len(self.content)

    def accept_put(self, storage):
        storage.put_blob(self)

    @classmethod
    def accept_get(cls, storage, key):
        storage.get_blob(cls, key)

    def accept_serializer(self, serializer):
        serializer.serialize_blob(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        deserializer.deserialize_blob(cls)
