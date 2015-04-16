#! /usr/bin/env python
"""
"""
from nit.core.diff import TreeDiff
from nit.core.log import getLogger
from nit.core.storage import Storable


logger = getLogger(__name__)


class Tree(Storable):
    """
    """

    class Node:
        """
        """

        def __init__(self, relative_file_path, key):
            self.path = relative_file_path
            self.key = key
            self.key_short = key[:6]

        def __str__(self):
            return str(self.path) + " " + str(self.key)

        def __repr__(self):
            return "Node('{}')".format(self)

        def __hash__(self):
            return hash(str(self))

        def __eq__(self, other):
            return hash(self) == hash(other)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __lt__(self, other):
            return self.path < other.path

    def __init__(self):
        self._nodeset = set()
        self._key_to_path = { }
        self._path_to_key = { }

    def __str__(self):
        return "\n".join(
            "{} {}".format(
                n.key, n.path
            ) for n in self.nodes
        )

    def accept_put(self, storage):
        storage.put_tree(self)

    def accept_serializer(self, serializer):
        serializer.serialize_tree(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_tree(cls)

    @property
    def node_set(self):
        return self._nodeset

    @property
    def key_set(self):
        return set([n.key for n in self._nodeset])

    @property
    def file_set(self):
        return set([n.path for n in self._nodeset])

    @property
    def key_to_node(self):
        return {
            node.key: node for node in self._nodeset
        }

    @property
    def file_to_node(self):
        return {
            node.path: node for node in self._nodeset
        }

    @property
    def nodes(self):
        return sorted(
            self._nodeset,
            key=lambda node: node.path
        )

    def add_node(self, tree_node):
        if tree_node in self._nodeset:
            return False
        existing_node = self.file_to_node.get(tree_node.path)
        if existing_node:
            self.remove_node(existing_node)
        self._nodeset.add(tree_node)
        self._key_to_path[tree_node.key] = tree_node.path
        self._path_to_key[tree_node.path] = tree_node.key
        return True

    def remove_node(self, tree_node):
        self._nodeset.remove(tree_node)
        del self._key_to_path[tree_node.key]
        del self._path_to_key[tree_node.path]

    def diff(self, other):
        return TreeDiff(self, other)
