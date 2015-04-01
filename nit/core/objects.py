#! /usr/bin/env python
"""
"""
import hashlib


class BaseObject:
    """
    An object that can be stored in a repository.
    """

    @property
    def key(self):
        """
        The identifier used to retrieve the same object using `get`.
        """
        raise NotImplementedError("key")

    def put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument.
        """
        raise NotImplementedError("put")

    @classmethod
    def get(cls, storage, key):
        """
        Accept method for a storage visitor retrieving an object.

        Should call the appropriate method on `storage` with
        `self` and `key` as the arguments and return the result.
        """
        raise NotImplementedError("get")

    def serialize(self, serializer):
        """
        Accept method for a serialization visitor storing the object.

        Should call a sequence of appropriate methods on `serializer`
        such as `write_bytes`, `write_string`, etc.
        """
        raise NotImplementedError("serialize")

    @classmethod
    def deserialize(cls, deserializer):
        """
        Accept method for a serialization visitor retrieving an object.

        Should call a sequence of appropriate methods on `serializer`
        such as `read_bytes`, `read_string`, etc.

        :return (cls): Deserialized instance of this class
        """
        raise NotImplementedError("deserialize")


class BaseBlob(BaseObject):
    """
    A Binary Large OBject, usually a representation of the raw bytes
    of a file in the filesystem.
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
