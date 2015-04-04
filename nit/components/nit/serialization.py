#! /usr/bin/env python
"""
"""
from nit.core.serialization import BaseSerializer
from nit.components.nit.blob import NitBlob


class NitSerializer(BaseSerializer):

    """
    """

    def serialize_blob(self, blob):
        self.serialize_signature("blob", len(blob))
        self.write_bytes(blob.content)

    def deserialize_blob(self):
        return NitBlob(self.read_bytes())
