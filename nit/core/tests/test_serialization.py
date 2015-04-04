#! /usr/bin/env python
"""
"""
import io
from unittest import TestCase

from nit.core.serialization import NitSerializer
from nit.core.storage import StorableBlob

class NitSerializerTests(TestCase):

    """
    """

    HELLO = b"hello"
    SERIALIZER_CLS = NitSerializer

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

    def test_serialize_then_deserialize(self):
        blob = StorableBlob(self.HELLO)
        self.serializer.serialize(blob)

        self.stream.seek(0)

        actual_blob = self.serializer.deserialize()
        self.assertEqual(len(blob), len(actual_blob))
        self.assertEqual(blob.content, actual_blob.content)
        self.assertEqual(blob.key, actual_blob.key)
