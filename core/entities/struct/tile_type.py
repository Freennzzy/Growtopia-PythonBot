from dataclasses import dataclass
from datetime import timedelta
from typing import List, Union

@dataclass
class FishInfo:
    fish_item_id: int
    lbs: int

@dataclass
class SilkWormColor:
    a: int
    r: int
    g: int
    b: int

@dataclass
class PetBattleCageExtra:
    damage: int
    pet: List[int]

@dataclass
class StorageBlockItemInfo:
    id: int
    amount: int

@dataclass
class CookingOvenIngredientInfo:
    item_id: int
    time_added: int

@dataclass
class CyBotCommandData:
    command_id: int
    is_command_used: int

# Tile Extra
@dataclass
class Basic:
    pass

@dataclass
class Door:
    text: str
    owner_uid: int

@dataclass
class Sign:
    text: str
    flags: int

@dataclass
class Lock:
    settings: int
    owner_uid: int
    access_count: int
    access_uids: List[int]
    minimum_level: int

@dataclass
class Seed:
    time_passed: int
    fruit_count: int
    ready_to_harvest: bool
    elapsed: timedelta

@dataclass
class Mailbox:
    unk_1: str
    unk_2: str
    unk_3: str
    unk_4: int

@dataclass
class Bulletin:
    unk_1: str
    unk_2: str
    unk_3: str
    unk_4: int

@dataclass
class Dice:
    symbol: int

@dataclass
class ChemicalSource:
    time_passed: int
    ready_to_harvest: bool
    elapsed: int

@dataclass
class AchievementBlock:
    unk_1: int
    tile_type: int

@dataclass
class HeartMonitor:
    user_id: int
    player_name: str

@dataclass
class DonationBox:
    unk_1: str
    unk_2: str
    unk_3: str
    unk_4: int

@dataclass
class Mannequin:
    text: str
    unk_1: int
    clothing_1 : int
    clothing_2 : int
    clothing_3 : int
    clothing_4 : int
    clothing_5 : int
    clothing_6 : int
    clothing_7 : int
    clothing_8 : int
    clothing_9 : int
    clothing_10 : int

@dataclass
class BunnyEgg:
    egg_placed: int

@dataclass
class GamePack:
    team: int

@dataclass
class GameGenerator:
    pass

@dataclass
class XenoniteCrystal:
    unk_1: int
    unk_2: int

@dataclass
class PhoneBooth:
    clothing_1 : int
    clothing_2 : int
    clothing_3 : int
    clothing_4 : int
    clothing_5 : int
    clothing_6 : int
    clothing_7 : int
    clothing_8 : int
    clothing_9 : int

@dataclass
class Crystal:
    unk_1: str

@dataclass
class CrimeInProgress:
    unk_1: str
    unk_2: int
    unk_3: int

@dataclass
class DisplayBlock:
    item_id: int

@dataclass
class VendingMachine:
    item_id: int
    price: int

@dataclass
class GivingTree:
    unk_1: int
    unk_2: int

@dataclass
class CountryFlag:
    country: str

@dataclass
class WeatherMachine:
    settings: int

@dataclass
class DataBedrock:
    pass

@dataclass
class Spotlight:
    pass

@dataclass
class FishTankPort:
    flags: int
    fishes: List[FishInfo]

@dataclass
class SolarCollector:
    unk_1: bytes

@dataclass
class Forge:
    temperature: int

@dataclass
class SteamOrgan:
    instrument_type: int
    note: int

@dataclass
class SilkWorm:
    type: int
    name: str
    age: int
    unk_1: int
    unk_2: int
    can_be_fed: int
    food_saturation: int
    water_saturation: int
    color: SilkWormColor
    sick_duration: int

@dataclass
class SewingMachine:
    bold_id_list: List[int]

@dataclass
class LobsterTrap:
    pass

@dataclass
class PaintingEasel:
    item_id: int
    label: str

@dataclass
class PetBattleCage:
    label: str
    unk_1: bytes
    extra: PetBattleCageExtra

@dataclass
class PetTrainer:
    name: str
    pet_total_count: int
    unk_1: int
    pets_id: List[int]

@dataclass
class SteamEngine:
    temperature: int

@dataclass
class LockBot:
    time_passed: int

@dataclass
class SpiritStorageUnit:
    ghost_jar_count: int

@dataclass
class Shelf:
    top_left_item_id: int
    top_right_item_id: int
    bottom_left_item_id: int
    bottom_right_item_id: int

@dataclass
class VipEntrance:
    unk_1: int
    owner_uid: int
    access_uids: List[int]

@dataclass
class ChallangeTimer:
    pass

@dataclass
class FishWallMount:
    label: str
    item_id: int
    lb: int

@dataclass
class Portrait:
    label: str
    unk_1: int
    unk_2: int
    unk_3: int
    unk_4: int
    face: int
    hat: int
    hair: int
    unk_5: int
    unk_6: int

@dataclass
class GuildWeatherMachine:
    unk_1: int
    gravity: int
    flags: int

@dataclass
class FossilPrepStation:
    unk_1: int

@dataclass
class DnaExtractor:
    pass

@dataclass
class Howler:
    pass

@dataclass
class ChemsynthTank:
    current_chem: int
    target_chem: int

@dataclass
class StorageBlock:
    items: List[StorageBlockItemInfo]

@dataclass
class CookingOven:
    temperature_level: int
    ingredients: List[CookingOvenIngredientInfo]

@dataclass
class AudioRack:
    note: str
    volume: int

@dataclass
class GeigerCharger:
    seconds_from_start: int
    seconds_to_complete: int
    charging_percent: int
    minutes_from_start: int
    minutes_to_complete: int

@dataclass
class AdventureBegins:
    pass

@dataclass
class TombRobber:
    pass

@dataclass
class BallonOMatic:
    total_rarity: int
    team_type: int

@dataclass
class TrainingPort:
    fish_lb: int
    fish_status: int
    fish_id: int
    fish_total_exp: int
    fish_level: int
    unk_1: int

@dataclass
class ItemSucker:
    item_id_to_suck: int
    item_amount: int
    flags: int
    limit: int

@dataclass
class CyBot:
    sync_timer: int
    activated: int
    command_datas: List[CyBotCommandData]

@dataclass
class GuildItem:
    pass

@dataclass
class Growscan:
    unk_1: int

@dataclass
class ContainmentFieldPowerNode:
    ghost_jar_count: int
    unk_1: List[int]

@dataclass
class SpiritBoard:
    unk_1: int
    unk_2: int
    unk_3: int

@dataclass
class StormyCloud:
    sting_duration: int
    is_solid: int
    non_solid_duration: int

@dataclass
class TemporaryPlatform:
    unk_1: int

@dataclass
class SafeVault:
    pass

@dataclass
class AngelicCountingCloud:
    is_raffling: int
    unk_1: int
    ascii_code: int

@dataclass
class InfinityWeatherMachine:
    interval_minutes: int
    weather_machine_list: List[int]

@dataclass
class PineappleGuzzler:
    pass

@dataclass
class KrakenGalaticBlock:
    pattern_index: int
    unk_1: int
    r: int
    g: int
    b: int

@dataclass
class FriendsEntrance:
    owner_user_id: int
    unk_1: int
    unk_2: int

@dataclass
class TesseractManipulator:
    gems: int
    unk_1: int
    item_id: int
    unk_2: int

TileType = Union[
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
]