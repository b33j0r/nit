#! /usr/bin/env python
"""
"""

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

class TreeDiff:

    """
    """

    def __init__(self, tree_from, tree_to):
        logger.trace("Creating TreeDiff")
        self.tree_from = tree_from
        self.tree_to = tree_to

        self.formatter = TreeDiffFormatter()

        (
            self.added_nodes,
            self.modified_nodes,
            self.removed_nodes
        ) = self._diff()

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
