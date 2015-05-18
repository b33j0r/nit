#! /usr/bin/env python
"""
"""
import io

from nit.core.serialization import BaseSerializer
from nit.components.nit.serialization import NitSerializer
from nit.core.objects.blob import Blob
from nit.core.tests.util import NitTestCase


class TestBaseSerializer(NitTestCase):

    """
    """

    HELLO = b"hello"
    SERIALIZER_CLS = BaseSerializer

    def setUp(self):
        self.stream = io.BytesIO()
        self.serializer = self.SERIALIZER_CLS(self.stream)

    def test_write_bytes_read_bytes(self):
        expected_b = self.HELLO
        self.serializer.write_bytes(expected_b)
        self.stream.seek(0)
        b = self.serializer.read_bytes()
        self.assertEqual(expected_b, b)

    def test_write_bytes_read_bytes_until_delimiter(self):
        expected_b = self.HELLO
        self.serializer.write_bytes(expected_b + b"\0")
        self.stream.seek(0)
        b = self.serializer.read_bytes_until()
        self.assertEqual(expected_b, b)

    def test_write_bytes_read_bytes_until_eof(self):
        expected_b = self.HELLO
        self.serializer.write_bytes(expected_b)
        self.stream.seek(0)
        b = self.serializer.read_bytes_until()
        self.assertEqual(expected_b, b)


class TestNitSerializer(TestBaseSerializer):

    """
    """

    SERIALIZER_CLS = NitSerializer

    def test_serialize_then_deserialize_blob(self):
        blob = Blob(self.HELLO)
        self.serializer.serialize(blob)

        self.stream.seek(0)

        actual_blob = self.serializer.deserialize()
        self.assertEqual(blob.content, actual_blob.content)
