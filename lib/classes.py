from __future__ import annotations

from typing import Optional, List

from .util import *


class Data:
    size: int
    offset: int

    def __init__(self, offset: int, size: int) -> None:
        self.offset = offset
        self.size = size


class Value:
    val: Any
    size: int
    offset: int
    raw: bytes
    display: str

    def __init__(self, offset: int, size: int, raw: bytes, value: Any) -> None:
        self.offset = offset
        self.size = size
        self.raw = raw
        self.val = value
        self.display = str(value)

    def __str__(self) -> str:
        v = self.display
        if v != str(self.val):
            v += ' [' + str(self.val) + ']'
        return v + ' (' + self.raw.hex(' ').upper() + ') @ ' + format(self.offset, 'x').upper()

    @staticmethod
    def value(value: Optional[Value]) -> Optional[Any]:
        return None if value is None else value.val

    @staticmethod
    def pretty(value: Optional[Value]) -> str:
        return 'None' if value is None else value.display


class Start(Data):
    number: Optional[Value]
    designator: Optional[Value]
    type: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.number = None
        self.designator = None
        self.type = None

    def __str__(self) -> str:
        return Value.pretty(self.number) + Value.pretty(self.designator)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Runway Number', self.number, indent)
        prnt('Runway Designation', self.designator, indent)
        prnt('Start Type', self.type, indent)


class TaxiwayPath(Data):
    number: Optional[Value]
    designator: Optional[Value]
    type: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.number = None
        self.designator = None
        self.type = None

    def __str__(self) -> str:
        return Value.pretty(self.type) + ' - ' + Value.pretty(self.number) + Value.pretty(self.designator)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Taxiway Type', self.type, indent)
        prnt('Runway Number', self.number, indent)
        prnt('Runway Designation', self.designator, indent)


class Runway(Data):
    primary_number: Optional[Value]
    secondary_number: Optional[Value]
    primary_designation: Optional[Value]
    secondary_designation: Optional[Value]
    heading: Optional[Value]
    primary_ils: Optional[Value]
    secondary_ils: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.primary_number = None
        self.secondary_number = None
        self.primary_designation = None
        self.secondary_designation = None
        self.heading = None
        self.primary_ils = None
        self.secondary_ils = None

    def __str__(self) -> str:
        return Value.pretty(self.primary_number) + Value.pretty(self.primary_designation) + ' / ' + Value.pretty(
            self.secondary_number) + Value.pretty(self.secondary_designation)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Primary Number', self.primary_number, indent)
        prnt('Primary Designation', self.primary_designation, indent)
        prnt('Secondary Number', self.secondary_number, indent)
        prnt('Secondary Designation', self.secondary_designation, indent)
        prnt('Heading', self.heading, indent)
        prnt('Primary ILS', self.primary_ils, indent)
        prnt('Secondary ILS', self.secondary_ils, indent)


class RunwayTransition(Data):
    number: Optional[Value]
    designator: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.number = None
        self.designator = None

    def __str__(self) -> str:
        return Value.pretty(self.number) + Value.pretty(self.designator)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Number', self.number, indent)
        prnt('Designator', self.designator, indent)


class Procedure(Data):
    name: Optional[Value]
    runwayTransitions: List[RunwayTransition]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.name = None
        self.runwayTransitions = []

    def __str__(self) -> str:
        return Value.pretty(self.name)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Primary Designation', self.name, indent)
        for runwayTransition in self.runwayTransitions:
            prnt('Runway Transition', runwayTransition, indent)
            runwayTransition.print(indent + 1)


class Airport(Data):
    name: Optional[Value]
    magvar: Optional[Value]
    ident: Optional[Value]
    runways: List[Runway]
    departures: List[Procedure]
    arrivals: List[Procedure]
    starts: List[Start]
    taxiwayPaths: List[TaxiwayPath]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.name = None
        self.magvar = None
        self.ident = None
        self.runways = []
        self.departures = []
        self.arrivals = []
        self.starts = []
        self.taxiwayPaths = []

    def __str__(self) -> str:
        if self.name is not None:
            return Value.pretty(self.name)
        else:
            return Value.pretty(self.ident)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Ident', self.ident, indent)
        prnt('Name', self.name, indent)
        prnt('Magvar', self.magvar, indent)
        for runway in self.runways:
            prnt('Runway', runway, indent)
            runway.print(indent+1)
        for arrival in self.arrivals:
            prnt('Arrival', arrival, indent)
            arrival.print(indent+1)
        for departure in self.departures:
            prnt('Departure', departure, indent)
            departure.print(indent+1)
        for start in self.starts:
            prnt('Start', start, indent)
            start.print(indent+1)
        for taxiwayPath in self.taxiwayPaths:
            prnt('Taxiway Path', taxiwayPath, indent)
            taxiwayPath.print(indent+1)


class Localizer(Data):
    width: Optional[Value]
    heading: Optional[Value]
    runway_designator: Optional[Value]
    runway_number: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.width = None
        self.heading = None
        self.runway_designator = None
        self.runway_number = None

    def __str__(self) -> str:
        return ''

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Runway Number', self.runway_number, indent)
        prnt('Runway Designator', self.runway_designator, indent)
        prnt('Heading', self.heading, indent)
        prnt('Width', self.width, indent)


class Dme(Data):
    range: Optional[Value]
    elevation: Optional[Value]
    latitude: Optional[Value]
    longitude: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.range = None
        self.elevation = None
        self.latitude = None
        self.longitude = None

    def __str__(self) -> str:
        return ''

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Latitude', self.latitude, indent)
        prnt('Longitude', self.longitude, indent)
        prnt('Elevation', self.elevation, indent)
        prnt('Range', self.range, indent)


class Glideslope(Data):
    pitch: Optional[Value]
    range: Optional[Value]
    elevation: Optional[Value]
    latitude: Optional[Value]
    longitude: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.pitch = None
        self.range = None
        self.elevation = None
        self.latitude = None
        self.longitude = None

    def __str__(self) -> str:
        return ''

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Latitude', self.latitude, indent)
        prnt('Longitude', self.longitude, indent)
        prnt('Elevation', self.elevation, indent)
        prnt('Range', self.range, indent)
        prnt('Pitch', self.pitch, indent)


class IlsVor(Data):
    region_airport: Optional[Value]
    type: Optional[Value]
    glideslope: Optional[Glideslope]
    name: Optional[Value]
    dme: Optional[Dme]
    latitude: Optional[Value]
    longitude: Optional[Value]
    localizer: Optional[Localizer]
    magvar: Optional[Value]
    ident: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.region_airport = None
        self.type = None
        self.glideslope = None
        self.name = None
        self.dme = None
        self.latitude = None
        self.longitude = None
        self.localizer = None
        self.magvar = None
        self.ident = None

    def __str__(self) -> str:
        if self.name is not None:
            return Value.pretty(self.name)
        else:
            return Value.pretty(self.ident)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Ident', self.ident, indent)
        prnt('Name', self.name, indent)
        prnt('Type', self.type, indent)
        prnt('Region/Airport', self.region_airport, indent)
        prnt('Magvar', self.magvar, indent)
        prnt('Latitude', self.latitude, indent)
        prnt('Longitude', self.longitude, indent)
        prnt('Localizer', self.localizer, indent)
        if self.localizer is not None:
            self.localizer.print(indent + 1)
        prnt('DME', self.dme, indent)
        if self.dme is not None:
            self.dme.print(indent + 1)
        prnt('Glideslope', self.glideslope, indent)
        if self.glideslope is not None:
            self.glideslope.print(indent + 1)


class Waypoint(Data):
    ident: Optional[Value]
    latitude: Optional[Value]
    longitude: Optional[Value]

    def __init__(self, offset: int, size: int) -> None:
        super().__init__(offset, size)
        self.ident = None
        self.latitude = None
        self.longitude = None

    def __str__(self) -> str:
        return Value.pretty(self.ident)

    def print(self, indent: int = 0) -> NoReturn:
        prnt('Ident', self.ident, indent)
        prnt('Latitude', self.latitude, indent)
        prnt('Longitude', self.longitude, indent)


class Bgl:
    ils_vors: List[IlsVor]
    airports: List[Airport]
    waypoints: List[Waypoint]
    file: str

    def __init__(self, file: str) -> None:
        self.file = file
        self.airports = []
        self.ils_vors = []
        self.waypoints = []

    def __str__(self) -> str:
        return str(self.file)
