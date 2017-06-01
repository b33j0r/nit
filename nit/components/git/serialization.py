import binascii
import hashlib
import os
import struct
import zlib
from io import BytesIO

from nit.components.nit.serialization import NitSerializer
from nit.core.log import getLogger
from nit.core.objects.index import Index
from nit.core.objects.tree import TreeNode

logger = getLogger(__name__)


def read_null_terminated_8_aligned_str(index_file):
    path = []
    i = 0
    while True:
        char = index_file.read(1)
        if char == b'\x00':
            if (i-1) % 8 == 0:
                break
        else:
            path.append(char)
        i += 1
    path_str = ''.join(str(c, encoding='utf-8') for c in path)
    return path_str


class GitSerializer(NitSerializer):

    """
    """

    CHUNK_SEP_BYTE = b"\0"
    FIELD_SEP_BYTE = b" "

    CHUNK_SEP_STR = CHUNK_SEP_BYTE.decode()
    FIELD_SEP_STR = FIELD_SEP_BYTE.decode()

    INDEX_HEADER_FMT = "!4sII"
    INDEX_ENTRY_HEADER_FMT = "!IIIIIIIIII20sH"

    def serialize_index(self, index, paths):
        with BytesIO() as f:
            f.write(struct.pack('!4s', b'DIRC'))
            f.write(struct.pack('!I', 2))
            f.write(struct.pack('!I', len(index)))

            for node in index.nodes_sorted:
                with BytesIO() as entry_f:
                    stat = (paths.project / node.path).stat()
                    bin_sha = binascii.unhexlify(node.key.encode())

                    path = str(node.path).encode()
                    path_len = min([len(path), 0xFFF])
                    path += b'\0'

                    flag = path_len

                    entry_f.write(struct.pack('!I', int(stat.st_ctime_ns // 10**9)))
                    entry_f.write(struct.pack('!I', int(stat.st_ctime_ns % 10**9)))
                    entry_f.write(struct.pack('!I', int(stat.st_mtime_ns // 10**9)))
                    entry_f.write(struct.pack('!I', int(stat.st_mtime_ns % 10**9)))
                    entry_f.write(struct.pack('!I', stat.st_dev))
                    entry_f.write(struct.pack('!I', stat.st_ino))
                    entry_f.write(struct.pack('!I', stat.st_mode))
                    entry_f.write(struct.pack('!I', stat.st_uid))
                    entry_f.write(struct.pack('!I', stat.st_gid))
                    entry_f.write(struct.pack('!I', stat.st_size))
                    entry_f.write(struct.pack('!20s', bin_sha))
                    entry_f.write(struct.pack('!H', flag))
                    entry_f.write(struct.pack('!{}s'.format(len(path)), path))

                    entry_b = entry_f.getvalue()
                    padding_amount = (8 - (len(entry_b) % 8))
                    if padding_amount == 8:
                        padding_amount = 0
                    padding = b'\0' * padding_amount

                    f.write(entry_b + padding)

            buffer = f.getvalue()
        index_sha = hashlib.sha1(buffer).hexdigest()
        index_sha_unhex = binascii.unhexlify(index_sha)
        buffer += index_sha_unhex
        print('index sha: {}'.format(index_sha))
        print('index index_sha_unhex: {}'.format(index_sha_unhex))
        self.write_bytes(buffer)

    def deserialize_index(self, index_cls):
        logger.trace("Deserializing Index")

        index = Index()

        header = self.read_bytes(12)
        signature, version, entry_count = struct.unpack(
            self.INDEX_HEADER_FMT, header
        )

        if signature != b'DIRC':
            raise Exception(
                'Index file has incorrect '
                'header (signature != DIRC)'
            )

        if version not in [2, 3, 4]:
            raise Exception(
                'Index file has incorrect '
                'header (version = {})'.format(version)
            )

        entry_header_len = struct.calcsize(self.INDEX_ENTRY_HEADER_FMT)

        for i in range(entry_count):
            rest = self.read_bytes(entry_header_len)
            rest = struct.unpack_from(self.INDEX_ENTRY_HEADER_FMT, rest)

            (
                ctime_s, ctime_n,
                mtime_s, mtime_m,
                dev, ino,
                mode,
                uid, gid,
                file_size,
                sha,
                permission
            ) = rest

            path = read_null_terminated_8_aligned_str(self.stream)
            sha = binascii.hexlify(sha)
            sha = str(sha, encoding='utf-8')

            logger.debug(
                ("Deserialized Index Node\n"
                 "            Sha:  {}\n"
                 "            Path: {}").format(
                    sha, path
                )
            )

            tree_node = TreeNode(path, sha, None)
            index.add_node(tree_node)

        return index
