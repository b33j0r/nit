#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractproperty

from nit.core.log import getLogger


logger = getLogger(__name__)


class TreeDiff(metaclass=ABCMeta):

    """
    Finds the differences between two trees. (Abstract
    base class.)
    """

    @abstractproperty
    def added(self):
        """
        Nodes with file paths in to_tree, but not from_tree

        :return (set):
        """
        pass

    @abstractproperty
    def removed(self):
        """
        Nodes with file paths in from_tree, but not to_tree

        :return (set):
        """
        pass

    @abstractproperty
    def modified(self):
        """
        Nodes sharing file paths in from_tree and to_tree
        but with differing key values

        :return (set):
        """
        pass

    @abstractproperty
    def unmodified(self):
        """
        Nodes perfectly matching in both trees

        :return (set):
        """
        pass


class BaseTreeDiff(TreeDiff):

    """
    Finds the differences between two trees.
    """

    def __init__(
            self,
            from_tree,
            to_tree
    ):
        self.from_nodes = set(from_tree or [])
        self.to_nodes = set(to_tree or [])

        # Associate paths with nodes
        self.from_paths = {
            n.path: n for n in self.from_nodes
        }
        self.from_paths_set = set(self.from_paths)

        self.to_paths = {
            n.path: n for n in self.to_nodes
        }
        self.to_paths_set = set(self.to_paths)

        # Associate keys with nodes
        self.from_keys = {
            n.key: n for n in self.from_nodes
        }
        self.from_keys_set = set(self.from_keys)

        self.to_keys = {
            n.key: n for n in self.to_nodes
        }
        self.to_keys_set = set(self.to_keys)

        # Find the nodes with paths in both trees
        self.both_paths_set = self.to_paths_set.intersection(
            self.from_paths_set
        )

    @property
    def added(self):
        """
        Nodes with file paths in to_tree, but not from_tree

        :return (set):
        """
        return {
            self.to_paths[k]
            for k in self.to_paths_set - self.from_paths_set
        }

    @property
    def removed(self):
        """
        Nodes with file paths in from_tree, but not to_tree

        :return (set):
        """
        return {
            self.from_paths[k]
            for k in self.from_paths_set - self.to_paths_set
        }

    @property
    def modified(self):
        """
        Nodes sharing file paths in from_tree and to_tree
        but with differing key values

        :return (set):
        """
        return {
            self.to_paths[k] for k in self.both_paths_set
            if self.to_paths[k].key != self.from_paths[k].key
        }

    @property
    def unmodified(self):
        """
        Nodes perfectly matching in both trees

        :return (set):
        """
        return self.from_nodes.intersection(
            self.to_nodes
        )
