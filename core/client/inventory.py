from core.utils import PacketReader

class InventoryItem:
    def __init__(self, item_id: int, amount: int, flag: int):
        self.id = item_id
        self.amount = amount
        self.flag = flag

    def __repr__(self):
        return f"InventoryItem(id={self.id}, amount={self.amount}, flag={self.flag})"

class Inventory:
    def __init__(self):
        self.size: int = 0
        self.item_count: int = 0
        self.items: dict[int, InventoryItem] = {}

    def parse(self, data: bytes):
        self.reset()
        r = PacketReader(data)

        r.skip(1)

        self.size = r.u32()
        self.item_count = r.u16()
        for _ in range(self.item_count):
            item_id = r.u16()
            amount = r.u8()
            flag = r.u8()
            self.items[item_id] = InventoryItem(item_id, amount, flag)

    def reset(self):
        self.size = 0
        self.item_count = 0
        self.items.clear()