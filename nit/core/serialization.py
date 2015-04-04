#! /usr/bin/env python
"""
"""

from abc import (
    ABCMeta,
    abstractmethod,
    abstractclassmethod
)


class Serializer(metaclass=ABCMeta):

    """
    """

    def __init__(self, stream):
        self.stream = stream

    @abstractmethod
    def serialize(self, serializable):
        pass

    @abstractmethod
    def deserialize(self):
        pass

    @abstractmethod
    def serialize_blob(self, blob):
        pass

    @abstractmethod
    def deserialize_blob(self, blob_cls):
        pass

    def write_bytes(self, b):
        self.stream.write(b)

    def read_bytes(self, n=None):
        return self.stream.read(n)

    def read_bytes_until(self, delimiter=b"\0"):
        byte_string = []

        while True:
            last_byte = self.stream.read(1)
            if last_byte in [delimiter, b""]:
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
        return b.decode(encoding=encoding)


class Serializable(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def accept_serializer(self, serializer):
        pass

    @abstractclassmethod
    def accept_deserializer(cls, deserializer):
        pass


class NitSerializer(Serializer):

    """
    """

    def serialize(self, serializable):
        serializable.accept_serializer(self)

    def deserialize(self):
        header = self.read_bytes_until().decode(
            encoding="ascii"
        )
        obj_type, obj_len = header.split(" ")
        obj_len = int(obj_len)
        if obj_type == "blob":
            from nit.core.storage import StorableBlob
            return self.deserialize_blob(StorableBlob)
        raise NotImplementedError(
            "Unknown object type '{}'".format(obj_type)
        )

    def serialize_blob(self, blob):
        self.write_string(
            "blob {blob_len}\0".format(
                blob_len=len(blob)
            ),
            encoding="ascii"
        )
        self.write_bytes(blob.content)

    def deserialize_blob(self, blob_cls):
        return blob_cls(self.read_bytes())
