#! /usr/bin/env python
"""
"""

class BaseSerializationStrategy:
    """
    """
    def __init__(self, file):
        self.file = file

    def write_bytes(self, bytes_):
        self.file.write(bytes_)

    def read_bytes(self):
        return self.file.read()
