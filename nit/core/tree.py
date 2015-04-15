#! /usr/bin/env python
"""
"""
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
        self._nodeset.add(tree_node)
        self._key_to_path[tree_node.key] = tree_node.path
        self._path_to_key[tree_node.path] = tree_node.key

    def remove_node(self, tree_node):
        self._nodeset.remove(tree_node)
        del self._key_to_path[tree_node.key]
        del self._path_to_key[tree_node.path]

    def diff(self, other):
        a_key_to_node = self.key_to_node
        b_key_to_node = other.key_to_node

        a_file_to_node = self.file_to_node
        b_file_to_node = other.file_to_node

        changes = other.node_set ^ self.node_set

        added_files = other.file_set - self.file_set
        removed_files = self.file_set - other.file_set

        modified_files = set([
            a_key_to_node.get(n.key, b_key_to_node.get(n.key)).path
            for n in changes
            if (
                n.path not in added_files and
                n.path not in removed_files
            )
        ])

        modified_nodes = sorted(set([
            other.file_to_node[path] for path in modified_files
        ]))

        added_nodes = sorted([
            b_file_to_node[f] for f in added_files
        ])

        removed_nodes = sorted([
            a_file_to_node[f] for f in removed_files
        ])

        logger.debug(
            "DIFF\n{}{}{}".format(
                ("\n" +
                 logger.Fore.GREEN +
                 "Added:\n" +
                 logger.Fore.RESET +
                 "\n".join(
                     "    {n.key} '{n.path}'".format(n=n)
                     for n in added_nodes
                 ) + "\n")
                if added_nodes else "",

                ("\n" +
                 logger.Fore.YELLOW +
                 "Modified:\n" +
                 logger.Fore.RESET +
                 "\n".join(
                     "    {n.key} '{n.path}'".format(n=n)
                     for n in modified_nodes
                 ) + "\n")
                if modified_nodes else "",

                ("\n" +
                 logger.Fore.RED +
                 "Removed:\n" +
                 logger.Fore.RESET +
                 "\n".join(
                     "    {n.key} '{n.path}'".format(n=n)
                     for n in removed_nodes
                 ) + "\n")
                if removed_nodes else ""
            )
        )

        return added_nodes, modified_nodes, removed_nodes
