import cbor2
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional
from core.entities.enums import TileFlag, WeatherType
from core.entities.struct import (
    TileType,
    Basic,
    Door,
    Sign,
    Lock,
    Seed,
    Mailbox,
    Bulletin,
    Dice,
    ChemicalSource,
    AchievementBlock,
    HeartMonitor,
    DonationBox,
    Mannequin,
    BunnyEgg,
    GamePack,
    GameGenerator,
    XenoniteCrystal,
    PhoneBooth,
    Crystal,
    CrimeInProgress,
    DisplayBlock,
    VendingMachine,
    GivingTree,
    CountryFlag,
    WeatherMachine,
    DataBedrock,
    Spotlight,
    FishTankPort,
    SolarCollector,
    Forge,
    SteamOrgan,
    SilkWorm,
    SewingMachine,
    LobsterTrap,
    PaintingEasel,
    PetBattleCage,
    PetTrainer,
    SteamEngine,
    LockBot,
    SpiritStorageUnit,
    Shelf,
    VipEntrance,
    ChallangeTimer,
    FishWallMount,
    Portrait,
    GuildWeatherMachine,
    FossilPrepStation,
    DnaExtractor,
    Howler,
    ChemsynthTank,
    StorageBlock,
    CookingOven,
    AudioRack,
    GeigerCharger,
    AdventureBegins,
    TombRobber,
    BallonOMatic,
    TrainingPort,
    ItemSucker,
    CyBot,
    GuildItem,
    Growscan,
    ContainmentFieldPowerNode,
    SpiritBoard,
    StormyCloud,
    TemporaryPlatform,
    SafeVault,
    AngelicCountingCloud,
    InfinityWeatherMachine,
    PineappleGuzzler,
    KrakenGalaticBlock,
    FriendsEntrance,
    TesseractManipulator
)
from core.manager import ItemDatabase
from core.utils import PacketReader

@dataclass(slots=True)
class Tile:
    foreground_item_id: int
    background_item_id: int
    parent_block_index: int
    flags_number: int
    flags: TileFlag
    x: int
    y: int
    tile_type: TileType

    @classmethod
    def new(
        cls,
        foreground_item_id: int,
        background_item_id: int,
        parent_block_index: int,
        flags: TileFlag,
        flags_number: int,
        x: int,
        y: int,
    ) -> "Tile":
        return cls(
            foreground_item_id=foreground_item_id,
            background_item_id=background_item_id,
            parent_block_index=parent_block_index,
            flags_number=flags_number,
            flags=flags,
            x=x,
            y=y,
            tile_type=Basic(),
        )

    def harvestable(self, item_database: ItemDatabase) -> bool:
        match self.tile_type:
            case Seed(ready_to_harvest=ready, elapsed=elapsed):
                if ready:
                    return True
                item = item_database.get_item(self.foreground_item_id)
                return elapsed.total_seconds() >= item.grow_time

            case ChemicalSource(ready_to_harvest=ready, elapsed=elapsed):
                if ready:
                    return True
                item = item_database.get_item(self.foreground_item_id)
                return elapsed >= item.grow_time

            case _:
                return False

@dataclass(slots=True)
class DroppedItem:
    id: int
    count: int
    flags: int
    uid: int
    x: float
    y: float


@dataclass(slots=True)
class Dropped:
    items_count: int = 0
    last_dropped_item_uid: int = 0
    items: List[DroppedItem] = field(default_factory=list)

    def clear(self) -> None:
        self.items_count = 0
        self.last_dropped_item_uid = 0
        self.items.clear()

@dataclass
class WorldBuilder:
    name: str = "EXIT"
    width: int = 0
    height: int = 0
    base_weather: WeatherType = WeatherType.Default
    current_weather: WeatherType = WeatherType.Default

    def with_name(self, name: str) -> "WorldBuilder":
        self.name = name
        return self

    def dimensions(self, width: int, height: int) -> "WorldBuilder":
        self.width = width
        self.height = height
        return self

    def weather(self, base: WeatherType, current: WeatherType) -> "WorldBuilder":
        self.base_weather = base
        self.current_weather = current
        return self

    def build(self) -> "World":
        tile_count = self.width * self.height
        return World(
            name=self.name,
            width=self.width,
            height=self.height,
            tile_count=tile_count,
            tiles=[],
            dropped=Dropped(),
            base_weather=self.base_weather,
            current_weather=self.current_weather,
            is_error=False,
            version=0,
            flags=0,
        )

@dataclass
class World:
    name: str
    width: int
    height: int
    tile_count: int
    tiles: List[Tile]
    dropped: Dropped
    base_weather: WeatherType
    current_weather: WeatherType
    is_error: bool
    version: int
    flags: int

    @classmethod
    def new(cls) -> "World":
        return WorldBuilder().build()

    def reset(self) -> None:
        self.name = "EXIT"
        self.width = 0
        self.height = 0
        self.tile_count = 0
        self.tiles.clear()
        self.dropped.clear()
        self.base_weather = WeatherType.Default
        self.current_weather = WeatherType.Default
        self.is_error = False
        self.version = 0
        self.flags = 0

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return self.tiles[y * self.width + x]

    def is_tile_harvestable(self, tile: Tile, item_db: ItemDatabase) -> bool:
        return tile.harvestable(item_db)

    def is_harvestable(self, x: int, y: int, item_db: ItemDatabase) -> bool:
        tile = self.get_tile(x, y)
        return tile.harvestable(item_db) if tile else False

    def is_valid(self) -> bool:
        return (
            self.width > 0
            and self.height > 0
            and not self.is_error
            and len(self.tiles) == self.width * self.height
        )

    def total_tiles(self) -> int:
        return self.width * self.height

    def update_tile(
        self,
        tile: Tile,
        reader: PacketReader,
        replace: bool,
        item_database: ItemDatabase,
    ) -> None:
        try:
            tile.foreground_item_id = reader.u16()
            tile.background_item_id = reader.u16()
            tile.parent_block_index = reader.u16()
            flags = reader.u16()
        except Exception as e:
            raise RuntimeError("Failed to read tile base data") from e

        tile.flags = TileFlag.from_bits(flags)
        tile.flags_number = flags
        #print(f"[DEBUG] Tile at ({tile.x}, {tile.y}): fg_id={tile.foreground_item_id}, bg_id={tile.background_item_id}, flags={tile.flags}")

        if (
            tile.foreground_item_id > item_database.item_count
            or tile.background_item_id > item_database.item_count
        ):
            self.is_error = True
            self.tiles.append(
                Tile.new(
                    0,
                    0,
                    0,
                    tile.flags,
                    tile.flags_number,
                    tile.x,
                    tile.y,
                )
            )
            raise RuntimeError(
                f"Item ID out of range at cursor position {reader.offset}: "
                f"foreground_id={tile.foreground_item_id}, "
                f"background_id={tile.background_item_id}, "
                f"max_item_count={item_database.item_count}, "
                f"tile position=({tile.x}, {tile.y})"
            )

        if tile.flags & TileFlag.HAS_PARENT:
            try:
                reader.u16()
            except Exception as e:
                raise RuntimeError("Failed to read parent data") from e

        if tile.flags & TileFlag.HAS_EXTRA_DATA:
            try:
                extra_tile_type = reader.u8()
            except Exception as e:
                raise RuntimeError("Failed to read extra tile type") from e

            self.get_extra_tile_data(
                tile,
                reader,
                extra_tile_type,
                item_database,
            )

        try:
            db_item = item_database.get_item(tile.foreground_item_id)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get item with ID {tile.foreground_item_id}"
            ) from e

        tiles_with_cbor_data = {
            15376,  # Party Projector
            8642,   # Bountiful Lattice Fence Roots
            15546,  # Auction Block
        }

        if (
            db_item.file_name.endswith(".xml")
            or tile.foreground_item_id in tiles_with_cbor_data
        ):
            try:
                cbor_size = reader.u32()
                cbor_raw = reader.read(cbor_size)
                value = cbor2.loads(cbor_raw)
                print(
                    f"Tile {tile.foreground_item_id} has CBOR value: {value}"
                )
            except Exception as e:
                raise RuntimeError("Failed to read CBOR tile data") from e

        index = tile.y * self.width + tile.x

        if replace:
            if index < len(self.tiles):
                self.tiles[index] = tile
            else:
                raise IndexError(f"Tile index {index} out of bounds")
        else:
            self.tiles.append(tile)

    def parse(self, data: bytes, item_database: ItemDatabase) -> None:
        self.reset()
        reader = PacketReader(data)

        self.version = reader.u16()
        if self.version < 0x19:
            self.is_error = True
            return

        self.flags = reader.u32()

        self.name = self.name = reader.string_u16()

        self.width = reader.u32()
        self.height = reader.u32()
        self.tile_count = reader.u32()
        print(f"[DEBUG] World {self.name}")

        reader.skip(5)

        if self.tile_count > 0xFE01:
            self.is_error = True
            return

        for i in range(self.tile_count):
            x = i % self.width
            y = i // self.width
            tile = Tile.new(0, 0, 0, TileFlag(0), 0, x, y)
            self.update_tile(tile, reader, False, item_database)

        reader.skip(12)

        self.dropped.items_count = reader.u32()
        self.dropped.last_dropped_item_uid = reader.u32()

        for _ in range(self.dropped.items_count):
            self.dropped.items.append(
                DroppedItem(
                    id=reader.u16(),
                    x=reader.f32(),
                    y=reader.f32(),
                    count=reader.u8(),
                    flags=reader.u8(),
                    uid=reader.u32(),
                )
            )
        print(f"[DEBUG] {self.dropped.items_count} dropped items")
        print(f"[DEBUG] Last dropped item UID: {self.dropped.last_dropped_item_uid}")
        print(f"[DEBUG] Dropped items: {self.dropped.items}")
        self.base_weather = WeatherType.from_id(reader.u16())
        reader.u16()
        self.current_weather = WeatherType.from_id(reader.u16())

    def get_extra_tile_data(self, tile: Tile, reader: PacketReader, extra_tile_type: int, item_database: ItemDatabase) -> None:
        match extra_tile_type:
            case 1:
                text = reader.string_u16()
                flags = reader.u8()
                print(f"[DEBUG] (SIGN) {text} | {flags} ")
                tile.tile_type = Sign(text, flags)
            case 2:
                text = reader.string_u16()
                owner_uid = reader.u32()
                print(f"[DEBUG] (DOOR) {text} | {owner_uid}")
                tile.tile_type = Door(text, owner_uid)
            case 3:
                print(f"[DEBUG] Lock at ({tile.x}, {tile.y})")

                settings = reader.u8()
                owner_uid = reader.u32()
                access_count = reader.u32()

                access_uids: list[int] = []
                for _ in range(access_count):
                    access_uids.append(reader.u32())

                minimum_level = reader.u8()

                reader.read(7)
                if tile.foreground_item_id == 5814:
                    reader.skip(16)

                tile.tile_type = Lock(
                    settings=settings,
                    owner_uid=owner_uid,
                    access_count=access_count,
                    access_uids=access_uids,
                    minimum_level=minimum_level,
                )

                print(
                    f"[DEBUG] (LOCK) owner={owner_uid} "
                    f"access_count={access_count} "
                    f"uids={access_uids} "
                    f"min_level={minimum_level}"
                )
            case 4:
                time_passed = reader.u32()
                fruit_count = reader.u8()
                item = item_database.get_item(tile.foreground_item_id)
                ready_to_harvest = time_passed >= item.grow_time
                elapsed = timedelta(seconds=time_passed)
                print(f"[DEBUG] (SEED) Item: {item}, fruit: {fruit_count}, time: {time_passed}, is ready: {ready_to_harvest}")
                tile.tile_type = Seed(
                    time_passed,
                    fruit_count,
                    ready_to_harvest,
                    elapsed,
                )
            case 6:
                unk_1 = reader.string_u16()
                unk_2 = reader.string_u16()
                unk_3 = reader.string_u16()
                unk_4 = reader.u8()
                tile.tile_type = Mailbox(
                    unk_1,
                    unk_2,
                    unk_3,
                    unk_4
                )
            case 7:
                unk_1 = reader.string_u16()
                unk_2 = reader.string_u16()
                unk_3 = reader.string_u16()
                unk_4 = reader.u8()
                tile.tile_type = Bulletin(
                    unk_1,
                    unk_2,
                    unk_3,
                    unk_4
                )
            case 8:
                symbol = reader.u8()
                tile.tile_type = Dice(symbol)
            case 9:
                time_passed = reader.u32()
                item = item_database.get_item(tile.foreground_item_id)
                ready_to_harvest = time_passed >= item.grow_time
                elapsed = timedelta(seconds=time_passed)
                tile.tile_type = ChemicalSource(
                    time_passed,
                    ready_to_harvest,
                    elapsed
                )
            case 10:
                unk_1 = reader.u32()
                tile_type = reader.u8()
                tile.tile_type = AchievementBlock(
                    unk_1,
                    tile_type
                )
            case 11:
                user_id = reader.u32()
                player_name = reader.string_u8()
                print(f"[DEBUG] (HEART MONITOR) {player_name} ({user_id})")
                tile.tile_type = HeartMonitor(
                    user_id,
                    player_name
                )
            case 12:
                unk_1 = reader.string_u16()
                unk_2 = reader.string_u16()
                unk_3 = reader.string_u16()
                unk_4 = reader.u8()
                tile.tile_type = DonationBox(
                    unk_1,
                    unk_2,
                    unk_3,
                    unk_4
                )
            case 14:
                text = reader.string_u16()
                unk_1 = reader.u8()
                clothing_1 = reader.u32()
                clothing_2 = reader.u16()
                clothing_3 = reader.u16()
                clothing_4 = reader.u16()
                clothing_5 = reader.u16()
                clothing_6 = reader.u16()
                clothing_7 = reader.u16()
                clothing_8 = reader.u16()
                clothing_9 = reader.u16()
                clothing_10 = reader.u16()
                print(f"[DEBUG] (MANNEQUIN) {text} | {unk_1} | {clothing_1} | {clothing_2} | {clothing_3} | {clothing_4} | {clothing_5} | {clothing_6} | {clothing_7} | {clothing_8} | {clothing_9} | {clothing_10}")
                tile.tile_type = Mannequin(
                    text,
                    unk_1,
                    clothing_1,
                    clothing_2,
                    clothing_3,
                    clothing_4,
                    clothing_5,
                    clothing_6,
                    clothing_7,
                    clothing_8,
                    clothing_9,
                    clothing_10
                )
            case 15:
                egg_placed = reader.u32()
                tile.tile_type = BunnyEgg(
                    egg_placed
                )
            case 16:
                team = reader.u8()
                tile.tile_type = GamePack(
                    team
                )
            case 17:
                tile.tile_type = GameGenerator()
            case 18:
                unk_1 = reader.u8()
                unk_2 = reader.u32()
                tile.tile_type = XenoniteCrystal(
                    unk_1,
                    unk_2
                )
            case 19:
                clothing_1 = reader.u16()
                clothing_2 = reader.u16()
                clothing_3 = reader.u16()
                clothing_4 = reader.u16()
                clothing_5 = reader.u16()
                clothing_6 = reader.u16()
                clothing_7 = reader.u16()
                clothing_8 = reader.u16()
                clothing_9 = reader.u16()
                tile.tile_type = PhoneBooth(
                    clothing_1,
                    clothing_2,
                    clothing_3,
                    clothing_4,
                    clothing_5,
                    clothing_6,
                    clothing_7,
                    clothing_8,
                    clothing_9
                )
            case 20:
                unk_1 = reader.string_u16()
                tile.tile_type = Crystal(
                    unk_1
                )
            case 21:
                unk_1 = reader.string_u16()
                unk_2 = reader.u32()
                unk_3 = reader.u8()
                tile.tile_type = CrimeInProgress(
                    unk_1,
                    unk_2,
                    unk_3
                )
            case 23:
                item_id = reader.u32()
                print(f"[DEBUG] (DISPLAY BLOCK) {item_id}")
                tile.tile_type = DisplayBlock(item_id)
            case 24:
                item_id = reader.u32()
                price = reader.i32()
                print(f"[DEBUG] (VENDING MACHINE) item_id={item_id} | price={price}")
                tile.tile_type = VendingMachine(
                    item_id,
                    price
                )
            case 43:
                top_left_item_id = reader.u32()
                top_right_item_id = reader.u32()
                bottom_left_item_id = reader.u32()
                bottom_right_item_id = reader.u32()
                print(f"[DEBUG] (SHELF) {top_left_item_id} | {top_right_item_id} | {bottom_left_item_id} | {bottom_right_item_id}")
                tile.tile_type = Shelf(
                    top_left_item_id,
                    top_right_item_id,
                    bottom_left_item_id,
                    bottom_right_item_id
                )
            case _:
                print(f"[DEBUG] Unknown extra tile type: {extra_tile_type} at fg_id={tile.foreground_item_id}, position=({tile.x}, {tile.y})")
                tile.tile_type = Basic()