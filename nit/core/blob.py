#! /usr/bin/env python
"""
"""
from nit.core.storage import Storable


class Blob(Storable):

    """
    """

    def __init__(self, content_bytes):
        self._content_bytes = content_bytes

    def __str__(self):
        return self.content.decode()

    def accept_put(self, storage):
        storage.put_blob(self)

    def accept_serializer(self, serializer):
        serializer.serialize_blob(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_blob(cls)

    @property
    def content(self):
        return self._content_bytes
