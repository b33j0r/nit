#! /usr/bin/env python
"""
"""

class BaseSerializationStrategy:
    """
    """
    def __init__(self, file):
        self.file = file

    def write_bytes(self, b):
        self.file.write(b)

    def read_bytes(self):
        return self.file.read()

    def write_string(self, s, encoding="utf-8"):
        b = s.encode(encoding=encoding)
        self.write_bytes(b)

    def read_string(self, encoding="utf-8"):
        b = self.read_bytes()
        return b.decode(encoding=encoding)
