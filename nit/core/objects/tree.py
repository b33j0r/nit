#! /usr/bin/env python
"""
"""
from abc import abstractproperty, abstractmethod
from pathlib import Path
from nit.core.diff import BaseTreeDiff
from nit.core.log import getLogger
from nit.core.storage import Storable


logger = getLogger(__name__)


class TreeNode:
    """
    """

    def __init__(self, relative_file_path, key, stat):
        self.path = Path(relative_file_path)
        self.key = key
        self.stat = stat

    def __str__(self):
        return "{} {}".format(
            self.path, self.key
        )

    def __repr__(self):
        return "TreeNode('{}')".format(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return str(self.path) < str(other.path)


class Treeish(Storable):
    """
    """
    @abstractproperty
    def nodes_sorted(self):
        """
        """

    @abstractmethod
    def __iter__(self):
        pass


class Tree(Treeish):
    """
    Stores a tree of objects, particularly Blobs and
    child Trees. This almost always represents a sub-directory
    as part of a Commit.
    """

    Node = TreeNode

    def __init__(self, nodes=None):
        self._nodes = set(nodes or [])

    def __str__(self):
        return (
            "Tree Object\n"
            "{}\n\n"
        ).format(
            "\n".join(
                "    {} {}".format(
                    n.key, n.path
                ) for n in self.nodes_sorted
            )
        )

    def accept_put(self, storage):
        storage.put_tree(self)

    def accept_serializer(self, serializer):
        serializer.serialize_tree(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_tree(cls)

    @property
    def nodes_sorted(self):
        return sorted(
            iter(self),
            key=lambda node: str(node.path)
        )

    @property
    def nodes_by_path(self):
        return {
            n.path: n for n in self._nodes
        }

    def __iter__(self):
        return iter(self._nodes)

    def add_node(self, tree_node):
        if tree_node in self._nodes:
            return False
        if tree_node.path in self.nodes_by_path:
            self._nodes.remove(
                self.nodes_by_path[tree_node.path]
            )
        self._nodes.add(tree_node)
        return True

    def remove_node(self, tree_node):
        self._nodes.remove(tree_node)

    def diff(self, other):
        return BaseTreeDiff(self, other)

    def __len__(self):
        return len(self._nodes)
