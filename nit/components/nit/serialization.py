#! /usr/bin/env python
"""
"""
from datetime import datetime
from io import BytesIO

from nit.core.objects.tree import Tree
from nit.core.objects.index import Index
from nit.core.objects.blob import Blob
from nit.core.objects.commit import Commit
from nit.core.log import getLogger
from nit.core.serialization import BaseSerializer

logger = getLogger(__name__)


class NitSerializer(BaseSerializer):

    """
    """

    CHUNK_SEP_BYTE = b"\n"
    FIELD_SEP_BYTE = b" "

    CHUNK_SEP_STR = CHUNK_SEP_BYTE.decode()
    FIELD_SEP_STR = FIELD_SEP_BYTE.decode()

    obj_type_mapping = {
        "blob": Blob,
        "tree": Tree,
        "index": Index,
        "commit": Commit
    }

    def __init__(self, stream):
        super().__init__(stream)

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
            "{obj_type}{FIELD_SEP_STR}{obj_len}{CHUNK_SEP_STR}".format(
                obj_type=obj_type,
                obj_len=obj_len,
                FIELD_SEP_STR=self.FIELD_SEP_STR,
                CHUNK_SEP_STR=self.CHUNK_SEP_STR
            )
        )

    def deserialize_signature(self):
        signature = self.read_bytes_until(self.CHUNK_SEP_BYTE).decode()
        obj_type, obj_len = signature.split(self.FIELD_SEP_STR)
        obj_len = int(obj_len)
        return obj_len, obj_type

    def serialize_index(self, index, paths):
        logger.trace("Serializing Index")

        content = self._serialize_tree_to_bytes(index)

        self.serialize_signature("index", len(content))
        self.write_bytes(content)

    def deserialize_index(self, index_cls):
        logger.trace("Deserializing Index")

        index = self._deserialize_tree_from_bytes(index_cls)

        return index

    def serialize_blob(self, blob):
        # logger.trace("Serializing Blob")

        content = blob.content
        self.serialize_signature("blob", len(content))
        self.write_bytes(content)

    def deserialize_blob(self, blob_cls):
        logger.trace("Deserializing Blob")

        return blob_cls(self.read_bytes())

    def _serialize_tree_to_bytes(self, tree):
        with BytesIO() as memory_file:
            memory_serializer = self.__class__(memory_file)

            for node in tree.nodes_sorted:
                memory_serializer.write_string(
                    node.key + self.FIELD_SEP_STR
                )
                memory_serializer.write_string(
                    str(node.path) + self.CHUNK_SEP_STR
                )

                logger.trace(
                    ("Serialized Tree.Node:\n"
                     "    Key:  {}\n"
                     "    Path: {}").format(
                        node.key, node.path
                    )
                )

            memory_file.seek(0)
            content = memory_file.read()
        return content

    def serialize_commit(self, commit):
        logger.trace("Serializing Commit")

        with BytesIO() as memory_file:
            memory_serializer = self.__class__(memory_file)

            memory_serializer.write_string(
                commit.created_timestamp.isoformat() + self.CHUNK_SEP_STR
            )

            memory_serializer.write_string(
                commit.author + self.CHUNK_SEP_STR
            )

            memory_serializer.write_string(
                commit.parent_key + self.CHUNK_SEP_STR
            )

            memory_serializer.write_string(
                commit.tree_key + self.CHUNK_SEP_STR
            )

            memory_serializer.write_string(
                commit.message
            )

            logger.trace(
                ("Serialized Commit:\n"
                 "    Author:  {}\n"
                 "    Parent:  {}\n"
                 "    Tree:    {}\n\n"
                 "{}").format(
                    commit.author,
                    commit.parent_key,
                    commit.tree_key,
                    commit.message
                )
            )

            content = memory_file.getvalue()

        self.serialize_signature("commit", len(content))
        self.write_bytes(content)

    def deserialize_commit(self, commit_cls):
        logger.trace("Deserializing Commit")

        created_timestamp_str = self.read_bytes_until(
            self.CHUNK_SEP_BYTE
        ).decode()
        created_timestamp = datetime.strptime(
            created_timestamp_str, "%Y-%m-%dT%H:%M:%S.%f"
        )

        author = self.read_bytes_until(
            self.CHUNK_SEP_BYTE
        ).decode()

        parent_key = self.read_bytes_until(
            self.CHUNK_SEP_BYTE
        ).decode()

        tree_key = self.read_bytes_until(
            self.CHUNK_SEP_BYTE
        ).decode()

        message = self.read_bytes().decode()

        commit = commit_cls(
            parent_key, tree_key,
            message=message,
            created_timestamp=created_timestamp,
            author=author
        )
        return commit

    def serialize_tree(self, tree):
        logger.trace("Serializing Tree")

        content = self._serialize_tree_to_bytes(tree)

        self.serialize_signature("tree", len(content))
        self.write_bytes(content)

    def _deserialize_tree_from_bytes(self, tree_cls):
        tree = tree_cls()
        while True:
            key = self.read_bytes_until(
                self.FIELD_SEP_BYTE
            ).decode()
            if not key:
                break

            path = self.read_bytes_until(
                self.CHUNK_SEP_BYTE
            ).decode()

            logger.trace(
                ("Deserialized TreeNode:\n"
                 "    Key:  {}\n"
                 "    Path: {}").format(
                    key, path
                )
            )

            tree.add_node(tree_cls.Node(relative_file_path=path, key=key))
        return tree

    def deserialize_tree(self, tree_cls):
        logger.trace("Deserializing Tree")

        tree = self._deserialize_tree_from_bytes(tree_cls)

        return tree
