#! /usr/bin/env python
"""
"""

from abc import (
    ABCMeta,
    abstractmethod,
    abstractclassmethod
)


class Serializable(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def accept_serializer(self, serializer):
        """
        Accept method for a serializer visitor serializing an object.

        Should call the appropriate method on `serializer` with
        `self` as the only argument.
        """
        pass

    @abstractclassmethod
    def accept_deserializer(cls, deserializer):
        """
        Accept method for a deserializer visitor deserializing an object.

        Should call the appropriate method on `deserializer` with
        `cls` as the only argument and return the result.
        """
        pass


class Serializer(metaclass=ABCMeta):

    """
    Serializes objects to a stream.

    Each instance of a Serializer only writes to one stream.
    Implementations are responsible for determining how this
    is done. This allows different file formats to be used
    for the same basic hierarchy of primitives (Blob, Tree,
    Commit, etc).
    """

    def __init__(self, stream):
        self.stream = stream

    @abstractmethod
    def serialize(self, serializable):
        pass

    @abstractmethod
    def deserialize(self):
        pass


class BaseSerializer(Serializer):

    """
    """

    def write_bytes(self, b):
        self.stream.write(b)

    def read_bytes(self, n=None):
        return self.stream.read(n)

    def read_bytes_until(self, terminator=b"\0"):
        byte_string = []

        while True:
            last_byte = self.stream.read(1)
            if last_byte in [terminator, b""]:
                break
            byte_string.append(last_byte)

        byte_string = b"".join(byte_string)

        # bytes conversion is not necessary here, it's
        # used to provide a type-hint for IDEs
        return bytes(byte_string)

    def write_string(self, s, encoding="utf-8"):
        b = s.encode(encoding=encoding)
        self.write_bytes(b)

    def read_string(self, encoding="utf-8"):
        b = self.read_bytes()
        s = b.decode(encoding=encoding)
        return s

    def serialize(self, serializable):
        serializable.accept_serializer(self)

    def deserialize(self):
        obj_cls = self._deserialize_get_obj_cls()
        return obj_cls.accept_deserializer(self)

    def _deserialize_get_obj_cls(self):
        raise NotImplementedError("_deserialize_get_obj_cls")

    def serialize_index(self, index, paths):
        raise NotImplementedError("serialize_index")

    def deserialize_index(self, index_cls):
        raise NotImplementedError("deserialize_index")

    def serialize_commit(self, commit):
        raise NotImplementedError("serialize_commit")

    def deserialize_commit(self, commit_cls):
        raise NotImplementedError("deserialize_commit")

    def serialize_blob(self, blob):
        raise NotImplementedError("serialize_blob")

    def deserialize_blob(self, blob_cls):
        raise NotImplementedError("deserialize_blob")

    def serialize_tree(self, tree):
        raise NotImplementedError("serialize_tree")

    def deserialize_tree(self, tree_cls):
        raise NotImplementedError("deserialize_tree")
