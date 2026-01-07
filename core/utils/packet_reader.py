import ctypes
import struct

def read_u32(pointer):
    return ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32)).contents.value

class PacketReader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def skip(self, n: int):
        self.offset += n

    def u8(self) -> int:
        v = self.data[self.offset]
        self.offset += 1
        return v

    def u16(self) -> int:
        v = struct.unpack_from("<H", self.data, self.offset)[0]
        self.offset += 2
        return v

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.offset)[0]
        self.offset += 4
        return v