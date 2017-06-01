#! /usr/bin/env python
"""
"""

from nit.core.objects.tree import Tree


class Index(Tree):

    """
    """

    def accept_put(self, storage):
        storage.put_index(self)

    def accept_serializer(self, serializer):
        raise NotImplementedError(
            'serialize_index should be called directly'
        )
        # serializer.serialize_index(self, None)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_index(cls)

    def add_node(self, tree_node):
        return super().add_node(tree_node)

    @classmethod
    def from_tree(cls, tree):
        index = cls()
        for node in tree:
            index.add_node(node)
        return index

    def to_tree(self):
        tree = Tree()
        for node in self:
            tree.add_node(node)
        return tree
