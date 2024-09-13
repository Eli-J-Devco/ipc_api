from gzip import compress, decompress
from base64 import b64encode, b64decode


def gzip_data(data: str) -> bytes:
    """
    Gzip data
    :author: nhan.tran
    :date: 16-07-2024
    :param data:
    :return: bytes
    """
    zipped_data = compress(data.encode("ascii"), compresslevel=9)
    b64_encoded_data = b64encode(zipped_data)
    return b64_encoded_data


def decompress_data(encoded_data: bytes) -> str:
    """
    Decompress data
    :author: nhan.tran
    :date: 16-07-2024
    :param encoded_data:
    :return: str
    """
    zipped_data = b64decode(encoded_data)
    data = decompress(zipped_data).decode("ascii")

    return data
