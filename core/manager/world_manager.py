import cbor2
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional
from core.entities.enums import TileFlag, WeatherType
from core.entities.struct import *
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

        self.base_weather = WeatherType(reader.u16()).name
        reader.u16()
        self.current_weather = WeatherType(reader.u16()).name

    def get_extra_tile_data(self, tile: Tile, reader: PacketReader, extra_tile_type: int, item_database: ItemDatabase) -> None:
        match extra_tile_type:
            case 1:  # Sign
                tile.tile_type = Sign(
                    reader.string_u16(),
                    reader.u8()
                )

            case 2:  # Door
                tile.tile_type = Door(
                    reader.string_u16(),
                    reader.u32()
                )

            case 3:  # Lock
                settings = reader.u8()
                owner_uid = reader.u32()
                access_count = reader.u32()
                access_uids = [reader.u32() for _ in range(access_count)]
                minimum_level = reader.u8()
                reader.read(7)

                if tile.foreground_item_id == 5814:
                    reader.skip(16)

                tile.tile_type = Lock(
                    settings,
                    owner_uid,
                    access_count,
                    access_uids,
                    minimum_level,
                )

            case 4:  # Seed
                time_passed = reader.u32()
                fruit_count = reader.u8()
                item = item_database.get_item(tile.foreground_item_id)
                ready_to_harvest = time_passed >= item.grow_time
                elapsed = timedelta(seconds=time_passed)

                tile.tile_type = Seed(
                    time_passed,
                    fruit_count,
                    ready_to_harvest,
                    elapsed,
                )

            case 6:  # Mailbox
                tile.tile_type = Mailbox(
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.u8(),
                )

            case 7:  # Bulletin
                tile.tile_type = Bulletin(
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.u8(),
                )

            case 8:  # Dice
                tile.tile_type = Dice(
                    reader.u8()
                )

            case 9:  # ChemicalSource
                time_passed = reader.u32()
                item = item_database.get_item(tile.foreground_item_id)
                ready_to_harvest = time_passed >= item.grow_time
                elapsed = timedelta(seconds=time_passed)

                if tile.foreground_item_id == 10656:
                    reader.skip(4)

                tile.tile_type = ChemicalSource(
                    time_passed,
                    ready_to_harvest,
                    elapsed,
                )

            case 10:  # AchievementBlock
                tile.tile_type = AchievementBlock(
                    reader.u32(),
                    reader.u8(),
                )

            case 11:  # HeartMonitor
                tile.tile_type = HeartMonitor(
                    reader.u32(),
                    reader.string_u16()
                )

            case 12:  # DonationBox
                tile.tile_type = DonationBox(
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.string_u16(),
                    reader.u8(),
                )

            case 14:  # Mannequin
                tile.tile_type = Mannequin(
                    reader.string_u16(),
                    reader.u8(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16()
                )

            case 15:  # BunnyEgg
                tile.tile_type = BunnyEgg(
                    reader.u32()
                )

            case 16:  # GamePack
                tile.tile_type = GamePack(
                    reader.u8()
                )

            case 17:  # GameGenerator
                tile.tile_type = GameGenerator()

            case 18:  # XenoniteCrystal
                tile.tile_type = XenoniteCrystal(
                    reader.u8(),
                    reader.u32()
                )

            case 19:  # PhoneBooth
                tile.tile_type = PhoneBooth(
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16(),
                    reader.u16()
                )

            case 20:  # Crystal
                tile.tile_type = Crystal(
                    reader.string_u16()
                )

            case 21:  # CrimeInProgress
                tile.tile_type = CrimeInProgress(
                    reader.string_u16(),
                    reader.u32(),
                    reader.u8(),
                )

            case 22:  # Spotlight
                tile.tile_type = Spotlight()

            case 23:  # DisplayBlock
                tile.tile_type = DisplayBlock(
                    reader.u32()
                )

            case 24:  # VendingMachine
                tile.tile_type = VendingMachine(
                    reader.u32(),
                    reader.i32()
                )

            case 25:  # FishTankPort
                flags = reader.u8()
                fish_count = reader.u32()
                fishes = [
                    FishInfo(reader.u32(), reader.u32())
                    for _ in range(fish_count // 2)
                ]
                tile.tile_type = FishTankPort(
                    flags,
                    fishes
                )

            case 26:  # SolarCollector
                tile.tile_type = SolarCollector(
                    reader.read(5)
                )

            case 27:  # Forge
                tile.tile_type = Forge(
                    reader.u32()
                )

            case 28:  # GivingTree
                tile.tile_type = GivingTree(
                    reader.u16(),
                    reader.u32()
                )

            case 30:  # SteamOrgan
                tile.tile_type = SteamOrgan(
                    reader.u8(),
                    reader.u32()
                )

            case 31:  # SilkWorm
                type_ = reader.u8()
                name = reader.string_u16()
                age = reader.u32()
                unk_1 = reader.u32()
                unk_2 = reader.u32()
                can_be_fed = reader.u8()
                food_saturation = reader.u32()
                water_saturation = reader.u32()
                color_raw = reader.u32()
                sick_duration = reader.u32()

                tile.tile_type = SilkWorm(
                    type_,
                    name,
                    age,
                    unk_1,
                    unk_2,
                    can_be_fed,
                    food_saturation,
                    water_saturation,
                    SilkWormColor(
                        (color_raw >> 24) & 0xFF,
                        (color_raw >> 16) & 0xFF,
                        (color_raw >> 8) & 0xFF,
                        color_raw & 0xFF,
                    ),
                    sick_duration,
                )

            case 32:  # SewingMachine
                count = reader.u16()
                tile.tile_type = SewingMachine(
                    [reader.u32() for _ in range(count)]
                )

            case 33:  # CountryFlag
                tile.tile_type = CountryFlag(
                    reader.string_u16()
                )

            case 34:  # LobsterTrap
                tile.tile_type = LobsterTrap()

            case 35:  # PaintingEasel
                tile.tile_type = PaintingEasel(
                    reader.u32(),
                    reader.string_u16()
                )

            case 36:  # PetBattleCage
                label = reader.string_u16()
                unk_1 = reader.u32()
                size = reader.u32()
                extra = reader.u32()
                tile.tile_type = PetBattleCage(
                    label,
                    unk_1,
                    extra
                )

            case 37:  # PetTrainer
                name = reader.string_u16()
                count = reader.u32()
                unk_1 = reader.u32()
                tile.tile_type = PetTrainer(
                    name,
                    count,
                    unk_1,
                    [reader.u32() for _ in range(count)]
                )


            case 38:  # SteamEngine
                tile.tile_type = SteamEngine(
                    reader.u32()
                )

            case 39:  # LockBot
                tile.tile_type = LockBot(
                    reader.u32()
                )

            case 40:  # WeatherMachine
                tile.tile_type = WeatherMachine(
                    reader.u32()
                )

            case 41:  # SpiritStorageUnit
                tile.tile_type = SpiritStorageUnit(
                    reader.u32()
                )

            case 42:  # DataBedrock
                reader.skip(21)
                tile.tile_type = DataBedrock()

            case 43:  # Shelf
                tile.tile_type = Shelf(
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                )

            case 43:  # Shelf
                tile.tile_type = Shelf(
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32()
                )

            case 44:  # VipEntrance
                tile.tile_type = VipEntrance(
                    reader.u8(),
                    reader.u32(),
                    [reader.u32() for _ in range(reader.u32())]
                )

            case 45:  # ChallangeTimer
                tile.tile_type = ChallangeTimer()

            case 47:  # FishWallMount
                tile.tile_type = FishWallMount(
                    reader.string_u16(),
                    reader.u32(),
                    reader.u8()
                )

            case 48:  # Portrait
                tile.tile_type = Portrait(
                    reader.string_u16(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u16(),
                    reader.u16(),
                )

            case 49:  # GuildWeatherMachine
                tile.tile_type = GuildWeatherMachine(
                    reader.u32(),
                    reader.u32(),
                    reader.u8()
                )

            case 50:  # FossilPrepStation
                tile.tile_type = FossilPrepStation(
                    reader.u32()
                )

            case 51:  # DnaExtractor
                tile.tile_type = DnaExtractor()

            case 52:  # Howler
                tile.tile_type = Howler()

            case 53:  # ChemsynthTank
                tile.tile_type = ChemsynthTank(
                    reader.u32(),
                    reader.u32()
                )

            case 54:  # StorageBlock
                size = reader.u16()
                items = []
                for _ in range(size // 13):
                    reader.skip(3)
                    id_ = reader.u32()
                    reader.skip(2)
                    amount = reader.u32()
                    items.append(StorageBlockItemInfo(id_, amount))
                tile.tile_type = StorageBlock(items)

            case 55:  # CookingOven
                temp = reader.u32()
                count = reader.u32()
                ingredients = [CookingOvenIngredientInfo(reader.u32(), reader.u32()) for _ in range(count)]
                reader.skip(12)
                tile.tile_type = CookingOven(temp, ingredients)

            case 56:  # AudioRack
                tile.tile_type = AudioRack(
                    reader.string_u16(),
                    reader.u32()
                )

            case 57:  # GeigerCharger
                raw = reader.u32()
                s = min(raw, 3600)
                tile.tile_type = GeigerCharger(
                    s, 3600 - s, s // 36, s // 60, max(0, 60 - s // 60)
                )

            case 58:  # AdventureBegins
                tile.tile_type = AdventureBegins()

            case 59:  # TombRobber
                tile.tile_type = TombRobber()

            case 60:  # BallonOMatic
                tile.tile_type = BallonOMatic(
                    reader.u32(),
                    reader.u8()
                )

            case 61:  # TrainingPort
                tile.tile_type = TrainingPort(
                    reader.u32(),
                    reader.u16(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32()
                )

            case 62:  # ItemSucker
                tile.tile_type = ItemSucker(
                    reader.u32(),
                    reader.u32(),
                    reader.u16(),
                    reader.u32()
                )

            case 63:  # CyBot
                sync = reader.u32()
                activated = reader.u32()
                count = reader.u32()
                commands = []
                for _ in range(count):
                    commands.append(CyBotCommandData(reader.u32(), reader.u32()))
                    reader.skip(7)
                tile.tile_type = CyBot(sync, activated, commands)

            case 65:  # GuildItem
                reader.skip(17)
                tile.tile_type = GuildItem()

            case 66:  # Growscan
                tile.tile_type = Growscan(
                    reader.u8()
                )

            case 67:  # ContainmentFieldPowerNode
                jars = reader.u32()
                size = reader.u32()
                tile.tile_type = ContainmentFieldPowerNode(
                    jars,
                    [reader.u32() for _ in range(size)]
                )

            case 68:  # SpiritBoard
                tile.tile_type = SpiritBoard(
                    reader.u32(),
                    reader.u32(),
                    reader.u32()
                )

            case 69:  # TesseractManipulator
                tile.tile_type = TesseractManipulator(
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                    reader.u32(),
                )

            case 72:  # StormyCloud
                tile.tile_type = StormyCloud(
                    reader.u32(),
                    reader.u32(),
                    reader.u32()
                )

            case 73:  # TemporaryPlatform
                tile.tile_type = TemporaryPlatform(
                    reader.u32()
                )

            case 74:  # SafeVault
                tile.tile_type = SafeVault()

            case 75:  # AngelicCountingCloud
                tile.tile_type = AngelicCountingCloud(
                    reader.u32(),
                    reader.u16(),
                    reader.u8()
                )

            case 77:  # InfinityWeatherMachine
                interval = reader.u32()
                tile.tile_type = InfinityWeatherMachine(
                    interval,
                    [reader.u32() for _ in range(reader.u32())]
                )

            case 79:  # PineappleGuzzler
                tile.tile_type = PineappleGuzzler()

            case 80:  # KrakenGalaticBlock
                tile.tile_type = KrakenGalaticBlock(
                    reader.u8(),
                    reader.u32(),
                    reader.u8(),
                    reader.u8(),
                    reader.u8()
                )

            case 81:  # FriendsEntrance
                tile.tile_type = FriendsEntrance(
                    reader.u32(),
                    reader.u16(),
                    reader.u16()
                )

            case _:
                print(
                    f"[WARN] Unknown tile extra {tile.tile_type} "
                    f"fg={tile.foreground_item_id} "
                    f"pos=({tile.x},{tile.y})"
                    f"offset={reader.offset}"
                )
                tile.tile_type = Basic()