from dataclasses import dataclass, field
from enum import IntFlag
from typing import Optional

from core.utils import PacketReader

SECRET = b"PBG892FXX982ABC*"

class ItemFlag(IntFlag):
    FLIPPABLE       = 0x1
    EDITABLE        = 0x2
    SEEDLESS        = 0x4
    PERMANENT       = 0x8
    DROPLESS        = 0x10
    NO_SELF         = 0x20
    NO_SHADOW       = 0x40
    WORLD_LOCKED    = 0x80
    BETA            = 0x100
    AUTO_PICKUP     = 0x200
    MOD_FLAG        = 0x400
    RANDOM_GROW     = 0x800
    PUBLIC          = 0x1000
    FOREGROUND      = 0x2000
    HOLIDAY         = 0x4000
    UNTRADEABLE     = 0x8000

    @classmethod
    def from_bits(cls, bits: int) -> "ItemFlag":
        return cls(bits)

@dataclass
class Item:
    id: int = 0
    flags: ItemFlag = ItemFlag(0)
    action_type: int = 0
    material: int = 0
    name: str = ""
    texture_file_name: str = ""
    texture_hash: int = 0
    cooking_ingredient: int = 0
    visual_effect: int = 0
    texture_x: int = 0
    texture_y: int = 0
    render_type: int = 0
    is_stripey_wallpaper: int = 0
    collision_type: int = 0
    block_health: int = 0
    drop_chance: int = 0
    clothing_type: int = 0
    rarity: int = 0
    max_item: int = 0
    file_name: str = ""
    file_hash: int = 0
    audio_volume: int = 0
    pet_name: str = ""
    pet_prefix: str = ""
    pet_suffix: str = ""
    pet_ability: str = ""
    seed_base_sprite: int = 0
    seed_overlay_sprite: int = 0
    tree_base_sprite: int = 0
    tree_overlay_sprite: int = 0
    base_color: int = 0
    overlay_color: int = 0
    ingredient: int = 0
    grow_time: int = 0
    is_rayman: int = 0
    extra_options: str = ""
    texture_path_2: str = ""
    extra_option2: str = ""
    punch_option: str = ""
    description: str = ""

@dataclass(slots=True)
class ItemDatabase:
    version: int = 0
    item_count: int = 0
    items: dict[int, Item] = field(default_factory=dict)
    loaded: bool = False

    def add_item(self, item: Item):
        self.items[item.id] = item

    def get_item_as_ref(self, id: int) -> Optional[Item]:
        return self.items.get(id)

    def get_item(self, id: int) -> Optional[Item]:
        item = self.items.get(id)
        return item if item is None else item

def load_from_memory(data: bytes) -> ItemDatabase:
    reader = PacketReader(data)
    
    db = ItemDatabase()
    db.version = reader.u16()
    db.item_count = reader.u32()

    for _ in range(db.item_count):
        item = read_item(reader, db.version)
        
        if item.id != len(db.items):
            raise ValueError("Item ID mismatch")
        db.add_item(item)

    db.loaded = True

    return db

def load_from_file(path: str) -> ItemDatabase:
    with open(path, "rb") as f:
        return load_from_memory(f.read())

def read_item(reader: PacketReader, version: int) -> Item:
    item = Item()
    item.id = reader.u32()
    item.flags = ItemFlag.from_bits(reader.u16())
    item.action_type = reader.u8()
    item.material = reader.u8()
    item.name = decrypt_item_name(reader, item.id)
    item.texture_file_name = read_str(reader)
    item.texture_hash = reader.u32()
    item.visual_effect = reader.u8()
    item.cooking_ingredient = reader.u32()
    item.texture_x = reader.u8()
    item.texture_y = reader.u8()
    item.render_type = reader.u8()
    item.is_stripey_wallpaper = reader.u8()
    item.collision_type = reader.u8()
    item.block_health = reader.u8()
    item.drop_chance = reader.u32()
    item.clothing_type = reader.u8()
    item.rarity = reader.u16()
    item.max_item = reader.u8()
    item.file_name = read_str(reader)
    item.file_hash = reader.u32()
    item.audio_volume = reader.u32()
    item.pet_name = read_str(reader)
    item.pet_prefix = read_str(reader)
    item.pet_suffix = read_str(reader)
    item.pet_ability = read_str(reader)
    item.seed_base_sprite = reader.u8()
    item.seed_overlay_sprite = reader.u8()
    item.tree_base_sprite = reader.u8()
    item.tree_overlay_sprite = reader.u8()
    item.base_color = reader.u32()
    item.overlay_color = reader.u32()
    item.ingredient = reader.u32()
    item.grow_time = reader.u32()
    reader.u16()
    item.is_rayman = reader.u16()
    item.extra_options = read_str(reader)
    item.texture_path_2 = read_str(reader)
    item.extra_option2 = read_str(reader)
    reader.skip(80)

    if version >= 11:
        item.punch_option = read_str(reader)
    if version >= 12:
        reader.skip(13)
    if version >= 13:
        reader.skip(4)
    if version >= 14:
        reader.skip(4)
    if version >= 15:
        reader.skip(25)
        _ = read_str(reader)
    if version >= 16:
        _ = read_str(reader)
    if version >= 17:
        reader.skip(4)
    if version >= 18:
        reader.skip(4)
    if version >= 19:
        reader.skip(9)
    if version >= 21:
        reader.skip(2)
    if version >= 22:
        item.description = read_str(reader)
    if version >= 23:
        reader.skip(4)
    if version >= 24:
        reader.skip(1)
    return item

def read_str(reader: PacketReader) -> str:
    length = reader.u16()
    chars = []
    for _ in range(length):
        chars.append(chr(reader.u8()))
    return "".join(chars)

def decrypt_item_name(reader: PacketReader, item_id: int) -> str:
    length = reader.u16()
    chars = []
    for i in range(length):
        secret_char = SECRET[(i + item_id) % len(SECRET)]
        input_char = reader.u8()
        chars.append(chr(input_char ^ secret_char))
    return "".join(chars)