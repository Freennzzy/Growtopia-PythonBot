import ctypes
import hashlib
from core.entities.enums import HashMode

def sha256(data: str) -> str:
    data = str(data)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def md5(data: str) -> str:
    data = str(data)
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def hash(data: bytes, mode, length: int = 0) -> int:
    hash_val = ctypes.c_uint32(0x55555555)

    if mode == HashMode.FixedLength:
        if length > 0:
            data_len = min(length, len(data))
            for i in range(data_len):
                b = data[i]
                hash_val.value = b + (hash_val.value >> 27) + (hash_val.value << 5)

    elif mode == HashMode.NullTerminated:
        for b in data:
            if b == 0:
                break
            hash_val.value = b + (hash_val.value >> 27) + (hash_val.value << 5)

    return hash_val.value