from nit.components.nit.serialization import NitSerializer


class GitSerializer(NitSerializer):

    """
    """

    CHUNK_SEP_BYTE = b"\0"
    FIELD_SEP_BYTE = b" "

    CHUNK_SEP_STR = CHUNK_SEP_BYTE.decode()
    FIELD_SEP_STR = FIELD_SEP_BYTE.decode()
