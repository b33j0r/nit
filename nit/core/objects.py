#! /usr/bin/env python
"""
"""
import hashlib


class BaseObject:
    """
    """

    @property
    def key(self):
        raise NotImplementedError("key")

    def put(self, storage):
        raise NotImplementedError("put")

    @classmethod
    def get(cls, storage, key):
        raise NotImplementedError("get")

    def serialize(self, serializer):
        raise NotImplementedError("serialize")

    @classmethod
    def deserialize(cls, deserializer):
        raise NotImplementedError("deserialize")


class BaseBlob(BaseObject):
    """
    """

    def __init__(self, content):
        self._content = content
        self._content_len = None

    @property
    def key(self):
        hash_object = hashlib.sha1(self.content)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    @property
    def content(self):
        return self._content

    def __len__(self):
        if self._content_len is None:
            self._content_len = len(self.content)
        return self._content_len

    def put(self, storage):
        storage.put_blob(self)

    @classmethod
    def get(cls, storage, key):
        return storage.get_blob(cls, key)

    def serialize(self, serializer):
        serializer.write_bytes(self.content)

    @classmethod
    def deserialize(cls, deserializer):
        content = deserializer.read_bytes()
        return cls(content)