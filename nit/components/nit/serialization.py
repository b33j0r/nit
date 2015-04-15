#! /usr/bin/env python
"""
"""
from io import BytesIO

from nit.core.log import getLogger
from nit.core.serialization import BaseSerializer
from nit.core.tree import Tree, TreeNode
from nit.components.nit.blob import NitBlob


logger = getLogger(__name__)


class NitSerializer(BaseSerializer):

    """
    """

    def serialize_blob(self, blob):
        logger.debug("Serializing Blob")

        content = blob.content
        self.serialize_signature("blob", len(content))
        self.write_bytes(content)

    def deserialize_blob(self):
        logger.debug("Deserializing Blob")

        return NitBlob(self.read_bytes())

    def serialize_tree(self, tree):
        logger.debug("Serializing Tree")

        with BytesIO() as memory_file:
            memory_serializer = self.__class__(memory_file)

            for node in tree.nodes:
                memory_serializer.write_string(node.key + "\0", encoding='ascii')
                memory_serializer.write_string(node.relative_file_path + "\0", encoding='ascii')

                logger.debug(
                    ("Serialized TreeNode:\n"
                     "    Key:  {}\n"
                     "    Path: {}").format(
                        node.key, node.relative_file_path
                    )
                )

            memory_file.seek(0)
            content = memory_file.read()

        self.serialize_signature("tree", len(content))
        self.write_bytes(content)

    def deserialize_tree(self):
        tree = Tree()

        logger.debug("Deserializing Tree")

        while True:
            key = self.read_bytes_until().decode(encoding='ascii')
            if not key:
                break

            path = self.read_bytes_until().decode(encoding='ascii')

            logger.debug(
                ("Deserialized TreeNode:\n"
                 "    Key:  {}\n"
                 "    Path: {}").format(
                    key, path
                )
            )

            tree.add_node(TreeNode(relative_file_path=path, key=key))

        return tree

    def serialize_index(self, index):
        self.serialize_tree(index)

    def deserialize_index(self):
        return self.deserialize_tree()
