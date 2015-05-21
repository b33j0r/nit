#! /usr/bin/env python
"""
"""
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty)

from nit.core.log import getLogger
from nit.core.serialization import Serializable

logger = getLogger(__name__)


class Storable(Serializable, metaclass=ABCMeta):

    """
    Something that can be stored, such as a blob (file) or a commit.
    """

    @abstractmethod
    def accept_put(self, storage):
        """
        Accept method for a storage visitor storing the object.

        Should call the appropriate put_ method on `storage`
        with `self` as the only argument and return the result.
        """


class ObjectStorage(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def get(self, keyish):
        """
        Returns an instance of `Storable` matching the given `keyish`

        :param keyish:
        :return (Storable):
        """

    def put(self, storable):
        """
        Writes a `Storable` to the ObjectStorage.

        :param storable (Storable): The object to insert
        :return key (str): The key of the object stored
        """
        return storable.accept_put(self)


class RefStorage(ObjectStorage, metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def get_ref(self, refspec):
        """
        Returns the value of the ref at `refspec`
        """

    @abstractmethod
    def put_ref(self, refspec, key):
        """
        Stores key in the ref at `refspec`
        """

    @abstractmethod
    def get_symbolic_ref(self, name):
        """
        Returns the ref referenced by `name`
        """

    @abstractmethod
    def put_symbolic_ref(self, name, ref):
        """
        Stores ref in the symbolic ref referenced by `name`
        """

    def resolve_ref(self, refspec):
        """
        Returns the object referenced by `refspec`
        """
        key = self.get_ref(refspec)
        return self.get(key)

    def resolve_symbolic_ref(self, name):
        """
        Returns the object referenced by `name`
        """
        refspec = self.get_symbolic_ref(name)
        return self.resolve_ref(refspec)


class MetadataStorage(metaclass=ABCMeta):

    """
    """

    @abstractmethod
    def get_config(self):
        """
        :return (Config): The current configuration
        """

    @abstractmethod
    def get_index(self):
        """
        :return (Index): The index
        """

    @abstractmethod
    def get_working_tree(self):
        """
        """


class Storage(RefStorage, MetadataStorage, metaclass=ABCMeta):

    """
    """

    @abstractproperty
    def exists(self):
        pass

    @abstractmethod
    def create(self, force=False):
        pass

    @abstractmethod
    def destroy(self, ignore_errors=True):
        pass
