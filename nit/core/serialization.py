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
        no arguments and return the result.
        """
        pass


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


class SerializerFactory(metaclass=ABCMeta):

    """
    Creates a serializer appropriate for a given `Serializable`,
    or a deserializer appropriate for a given byte stream.
    """

    @abstractmethod
    def get_serializer(self, serializable):
        pass

    @abstractmethod
    def get_deserializer(self, stream):
        pass


class BaseSerializer(Serializer):

    """
    """

    def serialize(self, serializable):
        serializable.accept_serializer(self)

    def deserialize(self):
        obj_len, obj_type = self.deserialize_signature()

        if obj_type == "blob":
            return self.deserialize_blob()
        else:
            raise NotImplementedError(
                "Unknown object type '{}'".format(obj_type)
            )

    def serialize_blob(self, blob):
        raise NotImplementedError("serialize_blob")

    def deserialize_blob(self):
        raise NotImplementedError("deserialize_blob")

    def serialize_signature(self, obj_type, obj_len):
        self.write_string(
            "{obj_type} {obj_len}\0".format(
                obj_type=obj_type,
                obj_len=obj_len
            ),
            encoding="ascii"
        )

    def deserialize_signature(self):
        signature = self.read_bytes_until().decode(
            encoding="ascii"
        )
        obj_type, obj_len = signature.split(" ")
        obj_len = int(obj_len)
        return obj_len, obj_type

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
