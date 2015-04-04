#! /usr/bin/env python
"""
"""
from abc import (
    ABCMeta,
    abstractmethod,
    abstractclassmethod,
    abstractproperty
)

from nit.core.serialization import Serializable


class Storable(Serializable, metaclass=ABCMeta):

    """
    Something that can be stored, such as a file or a commit.
    """

    @abstractproperty
    def key(self):
        """
        The identifier used to retrieve the same object using `get`.
        """
        pass

    @abstractmethod
    def accept_put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument.
        """
        pass

    @abstractclassmethod
    def accept_get(cls, storage, key):
        """
        Accept method for a storage visitor retrieving an object.

        Should call the appropriate method on `storage` with
        `self` and `key` as the arguments and return the result.
        """
        pass

    @abstractmethod
    def accept_serializer(self, serializer):
        """
        Accept method for a visitor serializing an object.

        Should call the appropriate method on `serializer` with
        `self` as the only argument.
        """
        pass

    @abstractmethod
    def accept_deserializer(cls, deserializer):
        """
        Accept method for a visitor deserializing an object.

        Should call the appropriate method on `deserializer` with
        no arguments and return the result.
        """
        pass


class Storage(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def create(self, force=False):
        pass

    @abstractmethod
    def destroy(self, ignore_errors=True):
        pass

    @abstractmethod
    def __contains__(self, key):
        pass

    @abstractmethod
    def put(self, storable):
        """
        Inserts a `Storable` into the Storage using the storable's `key`.

        :param storable (Storable): The object to insert
        """
        pass

    @abstractmethod
    def get(self, key):
        """
        Returns an instance of `Storable` having the given `key`

        :param key:
        :return (Storable):
        """
        pass

    @abstractmethod
    def put_blob(self, blob):
        pass

    @abstractmethod
    def get_blob(self, key):
        pass
