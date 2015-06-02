#! /usr/bin/env python
"""
"""
from nit.core.storage import Storable


class Blob(Storable):
    """
    An array of bytes, usually representing a file. Blobs
    are arguably the most important type of object that can
    be stored, because they contain the user's actual data,
    whereas things like commits represent metadata.

    A Blob does not care about things like file encoding,
    file attributes, or any other information except for the
    actual bytes represented.
    """

    def __init__(self, content_bytes):
        self._content_bytes = content_bytes

    def __str__(self):
        return self.content.decode()

    def accept_put(self, storage):
        return storage.put_blob(self)

    def accept_serializer(self, serializer):
        return serializer.serialize_blob(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_blob(cls)

    @property
    def content(self):
        """
        :return (bytes): The raw bytes of the Blob
        """
        return self._content_bytes
