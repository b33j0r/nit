#! /usr/bin/env python
"""
"""
from abc import ABCMeta, abstractproperty

from nit.core.log import getLogger


logger = getLogger(__name__)


class TreeDiffFormatter:

    """
    """

    def format_node(
            self,
            node,
            key_color=logger.Fore.LIGHTBLACK_EX,
            path_color=logger.Fore.RESET
    ):
        return (
            key_color + "{n.key}" +
            logger.Fore.RESET + " " +
            path_color + "{n.path}" +
            logger.Fore.RESET
        ).format(n=node)

    def format_nodes(
            self,
            nodes,
            name,
            header_color=logger.Fore.LIGHTWHITE_EX,
            key_color=logger.Fore.LIGHTBLACK_EX,
            path_color=logger.Fore.RESET
    ):
        if not nodes:
            return ""

        parts = [
            header_color,
            name,
            logger.Fore.RESET,
            "\n"
        ]

        node_parts = [
            self.format_node(
                node,
                key_color,
                path_color
            )
            for node in nodes
        ]
        node_parts_str = "\n".join(node_parts)
        parts.append(node_parts_str)
        parts.append("\n\n")
        return "".join(parts)


    def format(self, diff):
        s = "{}{}{}".format(
            self.format_nodes(
                diff.added_nodes,
                "Added",
                logger.Fore.GREEN
            ),
            self.format_nodes(
                diff.modified_nodes,
                "Modified",
                logger.Fore.YELLOW
            ),
            self.format_nodes(
                diff.removed_nodes,
                "Removed",
                logger.Fore.RED
            )
        )
        if s.endswith("\n\n"):
            s = s[:-1]

        if not s.strip():
            return "No changes detected"

        return s


class TreeDiff(metaclass=ABCMeta):

    """
    """

    @abstractproperty
    def added(self):
        """
        Nodes with file paths in index, but not head

        :return (set):
        """
        pass

    @abstractproperty
    def removed(self):
        """
        Nodes with file paths in head, but not index

        :return (set):
        """
        pass

    @abstractproperty
    def modified(self):
        """
        Nodes sharing file paths in head and index
        but with differing key values

        :return (set):
        """
        pass

    @abstractproperty
    def unmodified(self):
        """
        Nodes perfectly matching in head and index

        :return (set):
        """
        pass

    @abstractproperty
    def untracked(self):
        """
        Nodes with paths in stage but not in index

        :return (set):
        """
        pass

    @abstractproperty
    def ignored(self):
        """
        Nodes in stage but not index with ignore=True

        :return (set):
        """
        pass


class BaseTreeDiff(TreeDiff):

    def __init__(
            self,
            head_nodes,
            index_nodes,
            stage_nodes=None
    ):
        self.head_nodes = set(head_nodes)
        self.index_nodes = set(index_nodes)
        self.stage_nodes = set(stage_nodes or [])

        # Associate paths with nodes
        self.head_paths = {
            n.path: n for n in self.head_nodes
        }
        self.index_paths = {
            n.path: n for n in self.index_nodes
        }
        self.stage_paths = {
            n.path: n for n in self.stage_nodes
        }

        # Associate keys with nodes
        self.head_keys = {
            n.key: n for n in self.head_nodes
        }
        self.index_keys = {
            n.key: n for n in self.index_nodes
        }
        self.stage_keys = {
            n.key: n for n in self.stage_nodes
        }

    @property
    def added(self):
        """
        Nodes with file paths in index, but not head

        :return (set):
        """
        index_path_set = set(self.index_paths)
        head_path_set = set(self.head_paths)

        return {
            self.index_paths[k]
            for k in index_path_set - head_path_set
        }

    @property
    def removed(self):
        """
        Nodes with file paths in head, but not index

        :return (set):
        """
        index_path_set = set(self.index_paths)
        head_path_set = set(self.head_paths)

        return {
            self.head_paths[k]
            for k in head_path_set - index_path_set
        }

    @property
    def modified(self):
        """
        Nodes sharing file paths in head and index
        but with differing key values

        :return (set):
        """
        index_path_set = set(self.index_paths)
        head_path_set = set(self.head_paths)

        both_paths_set = index_path_set.intersection(
            head_path_set
        )

        return {
            self.index_paths[k]
            for k in both_paths_set
            if (
                self.head_paths[k].key
                != self.index_paths[k].key
            )
        }

    @property
    def unmodified(self):
        """
        Nodes perfectly matching in head and index

        :return (set):
        """
        index_path_set = set(self.index_paths)
        head_path_set = set(self.head_paths)

        both_paths_set = index_path_set.intersection(
            head_path_set
        )

        return {
            self.index_paths[k]
            for k in both_paths_set
            if (
                self.head_paths[k].key
                == self.index_paths[k].key
            )
        }

    @property
    def untracked_or_ignored(self):
        """
        Nodes with paths in stage but not in index

        :return (set):
        """
        index_path_set = set(self.index_paths)
        stage_path_set = set(self.stage_paths)

        stage_not_index = stage_path_set - index_path_set

        return {
            self.stage_paths[k]
            for k in stage_not_index
        }

    @property
    def untracked(self):
        """
        Nodes with paths in stage but not in index

        :return (set):
        """
        return {
            n for n in self.untracked_or_ignored if not n.ignore
        }

    @property
    def ignored(self):
        """
        Nodes in stage but not index with ignore=True

        :return (set):
        """
        return {
            n for n in self.untracked_or_ignored if n.ignore
        }


class TreeDiff:

    """
    """

    def __init__(self, tree_from, tree_to):
        logger.trace("Creating TreeDiff")
        self.tree_from = tree_from
        self.tree_to = tree_to

        self.formatter = TreeDiffFormatter()

        (
            self._added_nodes,
            self._modified_nodes,
            self._removed_nodes
        ) = self._diff()

    @property
    def added_nodes(self):
        return self._added_nodes

    @property
    def modified_nodes(self):
        return self._modified_nodes

    @property
    def removed_nodes(self):
        return self._removed_nodes

    def _diff(self):
        a_key_to_node = self.tree_from.key_to_node
        b_key_to_node = self.tree_to.key_to_node

        a_file_to_node = self.tree_from.file_to_node
        b_file_to_node = self.tree_to.file_to_node

        changes = self.tree_to.node_set ^ self.tree_from.node_set

        added_files = self.tree_to.file_set - self.tree_from.file_set
        removed_files = self.tree_from.file_set - self.tree_to.file_set

        modified_files = set([
            a_key_to_node.get(n.key, b_key_to_node.get(n.key)).path
            for n in changes
            if (
                n.path not in added_files and
                n.path not in removed_files
            )
        ])

        modified_nodes = sorted(set([
            self.tree_to.file_to_node[path] for path in modified_files
        ]))

        added_nodes = sorted([
            b_file_to_node[f] for f in added_files
        ])

        removed_nodes = sorted([
            a_file_to_node[f] for f in removed_files
        ])

        return added_nodes, modified_nodes, removed_nodes

    def __str__(self):
        logger.trace("Rendering string for TreeDiff")

        return self.formatter.format(self)
