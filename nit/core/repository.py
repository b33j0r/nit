#! /usr/bin/env python
"""
"""
from abc import abstractmethod, abstractproperty
from abc import ABCMeta


class Repository(metaclass=ABCMeta):

    """
    A high-level interface for interacting with a repository.
    (Abstract base class.)
    """

    @abstractproperty
    def exists(self):
        """
        :return (bool): True if the repository exists.
        """

    @abstractproperty
    def clean(self):
        """
        :return (bool): True if the working tree has no
                        changes versus the last commit.
        """

    @abstractmethod
    def create(self, force):
        """
        :param force (bool): Probably dangerous! If true,
                             creates a fresh repository.
                             Depending on the implementation,
                             you may lose your data!

                             This behavior was introduced for
                             iterative testing in the beginning
                             of development, and will be
                             removed at some point.

                             Git, for instance, does not delete
                             your data, but forces you to
                             `rm -rf .git`
        :return:
        """

    @abstractmethod
    def destroy(self):
        """
        DANGEROUS! Destroys the existing repository and all
        of its objects.

        This behavior was introduced for iterative testing
        in the beginning of development, and will be
        removed at some point.

        Git, for instance, does not delete your data, but
        forces you to `rm -rf .git`

        :return:
        """

    @abstractmethod
    def status(self):
        """
        TODO

        :return:
        """

    @abstractmethod
    def add(self, relative_file_path):
        """
        TODO

        :return:
        """

    @abstractmethod
    def commit(self):
        """
        TODO

        :return:
        """

    @abstractmethod
    def checkout(self, treeish):
        """
        TODO

        :param treeish:
        :return:
        """
