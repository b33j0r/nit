#! /usr/bin/env python
"""
"""
from nit.components.base.working_tree import BaseWorkingTree
from nit.components.git.status import GitStatusFormatter
from nit.components.git.storage import GitStorage
from nit.components.nit.ignore import NitIgnoreStrategy
from nit.components.nit.repository import NitRepository
from nit.components.nit.serialization import NitSerializer
from nit.core.log import getLogger
from nit.core.status import BaseStatusStrategy

logger = getLogger(__name__)


class GitRepository(NitRepository):

    """
    """

    def __init__(
            self,
            paths,
            storage_cls=GitStorage,
            serialization_cls=NitSerializer,
            ignore_cls=NitIgnoreStrategy,
            status_cls=BaseStatusStrategy,
            status_format_cls=GitStatusFormatter,
            working_tree_cls=BaseWorkingTree
    ):
        super().__init__(
            paths,
            storage_cls,
            serialization_cls,
            ignore_cls,
            status_cls,
            status_format_cls,
            working_tree_cls
        )
