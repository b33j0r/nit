#! /usr/bin/env python
"""
"""
from io import BytesIO

from nit.core.log import getLogger
from nit.core.serialization import BaseSerializer
from nit.core.tree import Tree
from nit.core.blob import Blob


logger = getLogger(__name__)


class NitSerializer(BaseSerializer):

    """
    """

    obj_type_mapping = {
        "blob": Blob,
        "tree": Tree
    }

    def _deserialize_get_obj_cls(self):
        obj_len, obj_type = self.deserialize_signature()

        try:
            return self.obj_type_mapping[obj_type]
        except KeyError:
            raise NotImplementedError(
                "Unknown object type '{}'".format(obj_type)
            )

    def serialize_signature(self, obj_type, obj_len):
        self.write_string(
            "{obj_type} {obj_len}\0".format(
                obj_type=obj_type,
                obj_len=obj_len
            ),
            encoding="ascii"
        )

    def deserialize_signature(self):
        signature = self.read_bytes_until().decode(
            encoding="ascii"
        )
        obj_type, obj_len = signature.split(" ")
        obj_len = int(obj_len)
        return obj_len, obj_type

    def serialize_blob(self, blob):
        logger.debug("Serializing Blob")

        content = blob.content
        self.serialize_signature("blob", len(content))
        self.write_bytes(content)

    def deserialize_blob(self, blob_cls):
        logger.debug("Deserializing Blob")

        return blob_cls(self.read_bytes())

    def serialize_tree(self, tree):
        logger.debug("Serializing Tree")

        with BytesIO() as memory_file:
            memory_serializer = self.__class__(memory_file)

            for node in tree.nodes:
                memory_serializer.write_string(
                    node.key + "\0", encoding='ascii'
                )
                memory_serializer.write_string(
                    node.relative_file_path + "\0", encoding='ascii'
                )

                logger.debug(
                    ("Serialized Tree.Node:\n"
                     "    Key:  {}\n"
                     "    Path: {}").format(
                        node.key, node.relative_file_path
                    )
                )

            memory_file.seek(0)
            content = memory_file.read()

        self.serialize_signature("tree", len(content))
        self.write_bytes(content)

    def deserialize_tree(self, tree_cls):
        tree = tree_cls()

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

            tree.add_node(tree_cls.Node(relative_file_path=path, key=key))

        return tree

    def serialize_index(self, index):
        self.serialize_tree(index)

    def deserialize_index(self, index_cls):
        return self.deserialize_tree(index_cls)
