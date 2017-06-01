import binascii
import struct
import zlib

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

    def deserialize_index(self, index_cls):
        logger.trace("Deserializing Index")

        header = self.read_bytes(12)
        signature, version, entry_count = struct.unpack("!4sII", header)

        if signature != b'DIRC':
            raise Exception('Index file has incorrect header (signature != DIRC)')
        if version != 2:
            raise Exception('Index file has incorrect header (version != 2)')

        entry_header_fmt = "!IIIIIIIIII20sh"
        entry_header_len = struct.calcsize(entry_header_fmt)

        index = Index()

        for i in range(entry_count):
            rest = self.read_bytes(entry_header_len)
            rest = struct.unpack_from(entry_header_fmt, rest)

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
            sha = binascii.b2a_hex(sha)
            sha = str(sha, encoding='utf-8')

            logger.debug(
                ("Deserialized Index Node:\n"
                 "    Sha:  {}\n"
                 "    Path: {}").format(
                    sha, path
                )
            )

            tree_node = TreeNode(path, sha)
            index.add_node(tree_node)

        return index
