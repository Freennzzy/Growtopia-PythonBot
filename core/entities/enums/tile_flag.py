from enum import IntFlag

class TileFlag(IntFlag):
    HAS_EXTRA_DATA          = 0x01
    HAS_PARENT              = 0x02
    WAS_SPLICED             = 0x04
    WILL_SPAWN_SEEDS_TOO    = 0x08
    IS_SEEDLING             = 0x10
    FLIPPED_X               = 0x20
    IS_ON                   = 0x40
    IS_OPEN_TO_PUBLIC       = 0x80
    BG_IS_ON                = 0x100
    FG_ALT_MODE             = 0x200
    IS_WATER                = 0x400
    GLUED                   = 0x800
    ON_FIRE                 = 0x1000
    PAINTED_RED             = 0x2000
    PAINTED_GREEN           = 0x4000
    PAINTED_BLUE            = 0x8000