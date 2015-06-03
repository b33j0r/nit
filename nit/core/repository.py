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
    def create(self):
        """
        :return (bool): True if the repository was created,
                        False if it was reinitialized.
        """

    @abstractmethod
    def status(self):
        """
        Reports the status of the local repository by
        taking diffs between the working tree, index,
        and HEAD commit.

        :return (Status):
        """

    @abstractmethod
    def add(self, relative_file_path):
        """
        Adds a file to the database and records it in the
        index.

        :return:
        """

    @abstractmethod
    def commit(self, message=None):
        """
        Saves the current index as a Commit object in the
        database and updates HEAD to point to it (usually
        via a branch under refs/heads)

        :return:
        """

    @abstractmethod
    def checkout(self, treeish):
        """
        Takes a diff between the current index and the
        index that the given treeish would have, and makes
        the necessary changes to make the working directory
        match.

        :param treeish: currently, a branch or a commit id
        :return:
        """
