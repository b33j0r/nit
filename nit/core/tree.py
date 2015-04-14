#! /usr/bin/env python
"""
"""
from nit.core.storage import Storable


class TreeNode:

    """
    """

    def __init__(self, relative_file_path, key):
        self.relative_file_path = relative_file_path
        self.key = key

    def __hash__(self):
        return hash(str(self.key) + "-" + str(self.relative_file_path))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class Tree(Storable):

    """
    """

    def __init__(self):
        self._nodes = set()

    def __str__(self):
        return "\n".join("    {} {}".format(n.key, n.relative_file_path) for n in self.nodes)

    def accept_put(self, storage):
        storage.put_tree(self)

    @classmethod
    def accept_get(cls, storage, key):
        storage.get_tree(cls, key)

    def accept_serializer(self, serializer):
        serializer.serialize_tree(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        deserializer.deserialize_tree(cls)

    @property
    def nodes(self):
        return sorted(
            self._nodes,
            key=lambda node: node.relative_file_path
        )

    def add_node(self, tree_node):
        self._nodes.add(tree_node)

    def remove_node(self, tree_node):
        self._nodes.remove(tree_node)
