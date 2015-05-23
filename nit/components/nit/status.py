#! /usr/bin/env python
"""
"""
from nit.core.log import getLogger
from nit.core.status import StatusFormatter


logger = getLogger(__name__)


class NitStatusFormatter(StatusFormatter):

    """
    """

    def format_node(
            self, node,
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

    def format_section(self, message, status_nodes):
        pass

    def format(self, diff):
        parts = [
            self.format_nodes(
                diff.added,
                "Added",
                logger.Fore.GREEN
            ),
            self.format_nodes(
                diff.removed,
                "Removed",
                logger.Fore.RED
            ),
            self.format_nodes(
                diff.modified,
                "Modified",
                logger.Fore.YELLOW
            ),
            self.format_nodes(
                diff.unstaged,
                "Unstaged",
                logger.Fore.LIGHTCYAN_EX
            ),
            self.format_nodes(
                diff.untracked,
                "Untracked",
                logger.Fore.LIGHTCYAN_EX
            )
        ]
        if False:
            parts += [
                self.format_nodes(
                    diff.ignored,
                    "Ignored",
                    logger.Fore.LIGHTBLACK_EX
                )
            ]
        s = "".join(parts)
        if s.endswith("\n\n"):
            s = s[:-1]

        if not s.strip():
            return "No changes detected"

        return s
