import ctypes
import struct

def read_u32(pointer):
    return ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32)).contents.value

class PacketReader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def remaining(self) -> int:
        return len(self.data) - self.offset

    def skip(self, n: int) -> None:
        self.offset += n

    def read(self, n: int) -> bytes:
        v = self.data[self.offset : self.offset + n]
        self.offset += n
        return v

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

    def i32(self) -> int:
        v = struct.unpack_from("<i", self.data, self.offset)[0]
        self.offset += 4
        return v


    def f32(self) -> float:
        v = struct.unpack_from("<f", self.data, self.offset)[0]
        self.offset += 4
        return v

    def string_u8(self) -> str:
        length = self.u8()
        raw = self.read(length)
        return raw.decode("utf-8", errors="ignore")

    def string_u16(self) -> str:
        length = self.u16()
        raw = self.read(length)
        return raw.decode("utf-8", errors="ignore")