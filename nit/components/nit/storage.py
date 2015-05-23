#! /usr/bin/env python
"""
"""
from nit.components.nit.serialization import NitSerializer
from nit.core.log import getLogger
from nit.components.base.storage import BaseStorage

logger = getLogger(__name__)


class NitStorage(BaseStorage):

    """
    """

    def __init__(
            self,
            paths,
            serialization_cls=NitSerializer
    ):
        super().__init__(
            paths,
            serialization_cls
        )
