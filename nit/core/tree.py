#! /usr/bin/env python
"""
"""
from pathlib import Path
from nit.core.diff import TreeDiff, BaseTreeDiff
from nit.core.log import getLogger
from nit.core.storage import Storable


logger = getLogger(__name__)


class TreeNode:
    """
    """

    def __init__(self, relative_file_path, key, ignore=False):
        self.path = Path(relative_file_path)
        self.key = key
        self.ignore = ignore

    def __str__(self):
        return "{} {} (ignore={})".format(
            self.path, self.key, self.ignore
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


class Tree(Storable):
    """
    """

    Node = TreeNode

    def __init__(self):
        self._nodes = set()

    def __str__(self):
        return (
            "Tree Object\n"
            "{}\n\n"
        ).format(
            "\n".join(
                "    {} {}".format(
                    n.key, n.path
                ) for n in self.nodes
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
    def nodes(self):
        return sorted(
            iter(self),
            key=lambda node: str(node.path)
        )

    def __iter__(self):
        return iter(self._nodes)

    def add_node(self, tree_node):
        if tree_node in self._nodes:
            return False
        self._nodes.add(tree_node)
        return True

    def remove_node(self, tree_node):
        self._nodes.remove(tree_node)

    def diff(self, other, stage=None):
        return BaseTreeDiff.from_trees(self, other, stage)
