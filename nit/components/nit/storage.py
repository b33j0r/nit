#! /usr/bin/env python
"""
"""
from nit.components.nit.serialization import NitSerializer
from nit.core.log import getLogger
from nit.core.storage import BaseStorage

logger = getLogger(__name__)


class NitStorage(BaseStorage):

    """
    """

    def __init__(
            self,
            paths_strategy,
            serialization_cls=NitSerializer,
            repo_dir_name=".nit"
    ):
        super().__init__(
            paths_strategy,
            serialization_cls,
            repo_dir_name
        )

