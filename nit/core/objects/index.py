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
        serializer.serialize_index(self)

    @classmethod
    def accept_deserializer(cls, deserializer):
        return deserializer.deserialize_index(cls)

    def add_node(self, tree_node):
        return super().add_node(tree_node)
