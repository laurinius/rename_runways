from enum import Enum


class RecordSize(Enum):
    AIRPORT = 0x44
    ILS_VOR = 0x28
    PROCEDURE = 0x14


class Subrecord(Enum):
    RUNWAY = 0xce
    ILS_LOCALIZER = 0x14
    DME = 0x16
    GLIDESLOPE = 0x15
    NAME = 0x19
    DEPARTURE = 0x42
    ARRIVAL = 0x48
    RUNWAY_TRANSITIONS = 0x46
    START = 0x11
    TAXIWAY_PATH_CONTAINER = 0xd4


class Section(Enum):
    AIRPORT = 0x03
    ILS_VOR = 0x13
    WAYPOINT = 0x22


class IlsVorType(Enum):
    VOR_TERMINAL = 1
    VOR_LOW = 2
    VOR_HIGH = 3
    ILS = 4
    VOR_VOT = 5


class StartType(Enum):
    UNKNOWN = 0x00
    RUNWAY = 0x01
    WATER = 0x02
    HELIPAD = 0x03
    TRACK = 0x04
