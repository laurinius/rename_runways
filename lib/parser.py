from typing import Callable

from .consts import *
from .classes import *


def parse_int(file: BinaryIO, offset: int, size: int) -> Value:
    barr = read(file, offset, size)
    return Value(offset, size, barr, to_int(barr))


def parse_float(file: BinaryIO, offset: int, size: int) -> Value:
    barr = read(file, offset, size)
    return Value(offset, size, barr, to_float(barr))


def parse_string(file: BinaryIO, offset: int, size: int, encoding: str = 'ascii') -> Value:
    barr = read(file, offset, size)
    return Value(offset, size, barr, to_string(barr, encoding))


def parse_name(file: BinaryIO, offset: int, size: int, encoding: str = 'ascii') -> Value:
    return parse_string(file, offset + 0x06, size - 6, encoding)
    # barr = read(file, offset + 0x06, size - 6)
    # return Value(offset, size, barr, to_string(barr))


def parse_ident(file: BinaryIO, offset: int, size: int, shift: bool = True) -> Value:
    value = parse_int(file, offset, size)
    value.val = decode_ident(value.val, shift)
    value.display = str(value.val)
    return value


def parse_longitude(file: BinaryIO, offset: int, size: int) -> Value:
    value = parse_int(file, offset, size)
    value.val = (value.val * (360.0 / (3 * 0x10000000))) - 180.0
    value.display = str(value.val)
    return value


def parse_latitude(file: BinaryIO, offset: int, size: int) -> Value:
    value = parse_int(file, offset, size)
    value.val = 90.0 - (value.val * (180.0 / (2 * 0x10000000)))
    value.display = str(value.val)
    return value


def parse_runway_designator(file: BinaryIO, offset: int, size: int) -> Value:
    value = parse_int(file, offset, size)
    return _parse_runway_designator(value)


def _parse_runway_designator(value: Value) -> Value:
    if value.val == 0:
        value.display = ''
    elif value.val == 1:
        value.display = 'L'
    elif value.val == 2:
        value.display = 'R'
    elif value.val == 3:
        value.display = 'C'
    elif value.val == 4:
        value.display = 'W'
    elif value.val == 5:
        value.display = 'A'
    elif value.val == 6:
        value.display = 'B'
    else:
        value.display = ''
    return value


def parse_runway_number(file: BinaryIO, offset: int, size: int) -> Value:
    value = parse_int(file, offset, size)
    if value.val == 0:
        value.display = ''
    elif value.val <= 36:
        value.display = str(value.val).zfill(2)
    elif value.val == 37:
        value.display = 'n'
    elif value.val == 38:
        value.display = 'ne'
    elif value.val == 39:
        value.display = 'e'
    elif value.val == 40:
        value.display = 'se'
    elif value.val == 41:
        value.display = 's'
    elif value.val == 42:
        value.display = 'sw'
    elif value.val == 43:
        value.display = 'w'
    elif value.val == 44:
        value.display = 'nw'
    else:
        value.display = ''
    return value


def parse_runway_transition(f: BinaryIO, offset: int, size: int) -> RunwayTransition:
    rt = RunwayTransition(offset, size)
    rt.number = parse_runway_number(f, offset + 0x7, 1)
    rt.designator = parse_runway_designator(f, offset + 0x8, 1)
    return rt


def parse_departure(f: BinaryIO, offset: int, size: int) -> Procedure:
    dep = Procedure(offset, size)
    dep.name = parse_string(f, offset + 0xc, 8)
    subrecord_end = size + offset
    subrecord_offset = offset + RecordSize.PROCEDURE.value
    while subrecord_offset < subrecord_end:
        subrecord_id = read_int(f, subrecord_offset, 2)
        subrecord_size = read_int(f, subrecord_offset + 0x02, 4)
        if subrecord_id == Subrecord.RUNWAY_TRANSITIONS.value:
            dep.runwayTransitions.append(parse_runway_transition(f, subrecord_offset, subrecord_size))
        subrecord_offset += subrecord_size
    return dep


def parse_arrival(f: BinaryIO, offset: int, size: int) -> Procedure:
    arr = Procedure(offset, size)
    arr.name = parse_string(f, offset + 0xc, 8)
    subrecord_end = size + offset
    subrecord_offset = offset + RecordSize.PROCEDURE.value
    while subrecord_offset < subrecord_end:
        subrecord_id = read_int(f, subrecord_offset, 2)
        subrecord_size = read_int(f, subrecord_offset + 0x02, 4)
        if subrecord_id == Subrecord.RUNWAY_TRANSITIONS.value:
            arr.runwayTransitions.append(parse_runway_transition(f, subrecord_offset, subrecord_size))
        subrecord_offset += subrecord_size
    return arr


def parse_runway(f: BinaryIO, offset: int, size: int) -> Runway:
    runway = Runway(offset, size)
    runway.heading = parse_float(f, offset + 0x28, 4)
    runway.primary_number = parse_runway_number(f, offset + 0x08, 1)
    runway.primary_designation = parse_runway_designator(f, offset + 0x09, 1)
    runway.primary_ils = parse_ident(f, offset + 0x0C, 4, False)
    runway.secondary_number = parse_runway_number(f, offset + 0x0A, 1)
    runway.secondary_designation = parse_runway_designator(f, offset + 0x0B, 1)
    runway.secondary_ils = parse_ident(f, offset + 0x10, 4, False)
    return runway


def parse_start(f: BinaryIO, offset: int, size: int) -> Start:
    start = Start(offset, size)
    start.number = parse_runway_number(f, offset + 0x6, 1)
    designator_and_type = read(f, offset + 0x7, 1)
    type = designator_and_type[0] >> 4
    designator = designator_and_type[0] & 0b1111
    start.designator = _parse_runway_designator(Value(offset + 0x7, 1, designator_and_type, designator))
    start.type = Value(offset + 0x7, 1, designator_and_type, type)
    start.type.display = StartType(start.type.val).name
    return start


def parse_airport(f: BinaryIO, offset: int, size: int) -> Airport:
    airport = Airport(offset, size)
    airport.runways = []
    airport.magvar = parse_float(f, offset + 0x24, 4)
    airport.ident = parse_ident(f, offset + 0x28, 4)
    subrecord_end = size + offset
    subrecord_offset = offset + RecordSize.AIRPORT.value
    while subrecord_offset < subrecord_end:
        subrecord_id = read_int(f, subrecord_offset, 2)
        subrecord_size = read_int(f, subrecord_offset + 0x02, 4)
        if subrecord_id == Subrecord.NAME.value:
            airport.name = parse_name(f, subrecord_offset, subrecord_size, 'utf8')
        if subrecord_id == Subrecord.RUNWAY.value:
            airport.runways.append(parse_runway(f, subrecord_offset, subrecord_size))
        if subrecord_id == Subrecord.DEPARTURE.value:
            airport.departures.append(parse_departure(f, subrecord_offset, subrecord_size))
        if subrecord_id == Subrecord.ARRIVAL.value:
            airport.arrivals.append(parse_arrival(f, subrecord_offset, subrecord_size))
        if subrecord_id == Subrecord.START.value:
            airport.starts.append(parse_start(f, subrecord_offset, subrecord_size))
        if subrecord_id == Subrecord.TAXIWAY_PATH_CONTAINER.value:
            airport.taxiwayPaths.extend(parse_taxiway_path_container(f, subrecord_offset, subrecord_size))
        subrecord_offset += subrecord_size
    return airport


def parse_taxiway_path_container(f: BinaryIO, offset: int, size: int) -> List[TaxiwayPath]:
    taxiway_paths = []
    rec_size = parse_int(f, offset + 0x2, 4)
    count = read_int(f, offset + 0x6, 2)
    next_offset = offset + 0x8
    i = 0
    while i < count:
        i += 1
        material_count = read_int(f, next_offset + 0x2c, 1)
        type_and_more = read(f, next_offset + 0x4, 1)
        type = type_and_more[0] & 0b1111

        if type == 0x2:
            taxiway_path = TaxiwayPath(next_offset, 48 + material_count * 44)
            taxiway_path.type = Value(next_offset + 0x4, 1, type_and_more, type)
            taxiway_path.number = parse_runway_number(f, next_offset + 0x5, 1)

            designator_and_more = read(f, next_offset + 0x3, 1)
            designator = designator_and_more[0] >> 4
            taxiway_path.designator = _parse_runway_designator(Value(next_offset + 0x3, 1, designator_and_more, designator))
            taxiway_paths.append(taxiway_path)

        next_offset = next_offset + 48 + material_count * 44
    return taxiway_paths


def parse_localizer(f: BinaryIO, offset: int, size: int) -> Localizer:
    localizer = Localizer(offset, size)
    localizer.runway_number = parse_runway_number(f, offset + 0x06, 1)
    localizer.runway_designator = parse_runway_designator(f, offset + 0x07, 1)
    localizer.heading = parse_float(f, offset + 0x08, 4)
    localizer.width = parse_float(f, offset + 0x0C, 4)
    return localizer


def parse_dme(f: BinaryIO, offset: int, size: int) -> Dme:
    dme = Dme(offset, size)
    dme.longitude = parse_longitude(f, offset + 0x08, 4)
    dme.latitude = parse_latitude(f, offset + 0x0C, 4)
    dme.elevation = parse_int(f, offset + 0x10, 4)
    dme.range = parse_float(f, offset + 0x14, 4)
    return dme


def parse_glideslope(f: BinaryIO, offset: int, size: int) -> Glideslope:
    glideslope = Glideslope(offset, size)
    glideslope.longitude = parse_longitude(f, offset + 0x08, 4)
    glideslope.latitude = parse_latitude(f, offset + 0x0C, 4)
    glideslope.elevation = parse_int(f, offset + 0x10, 4)
    glideslope.range = parse_float(f, offset + 0x14, 4)
    glideslope.pitch = parse_float(f, offset + 0x18, 4)
    return glideslope


def parse_region_airport(f: BinaryIO, offset: int, size: int) -> Value:
    barr = read(f, offset, size)
    val = to_int(barr)
    airport_val = val >> 11
    region_val = val & 0b00000000000000000000011111111111
    region = decode_ident(region_val, shift=False)
    airport = decode_ident(airport_val, shift=False)
    return Value(offset, size, barr, (region, airport))


def parse_ils_vor(f: BinaryIO, offset: int, size: int) -> IlsVor:
    ils_vor = IlsVor(offset, size)
    ils_vor.type = parse_int(f, offset + 0x06, 1)
    ils_vor.type.display = IlsVorType(ils_vor.type.val).name
    ils_vor.longitude = parse_longitude(f, offset + 0x08, 4)
    ils_vor.latitude = parse_latitude(f, offset + 0x0C, 4)
    ils_vor.magvar = parse_float(f, offset + 0x1C, 4)
    ils_vor.ident = parse_ident(f, offset + 0x20, 4)
    if ils_vor.type.val == IlsVorType.ILS.value:
        ils_vor.region_airport = parse_region_airport(f, offset + 0x24, 4)
    subrecord_end = size + offset
    subrecord_offset = offset + RecordSize.ILS_VOR.value
    while subrecord_offset < subrecord_end:
        subrecord_id = read_int(f, subrecord_offset, 2)
        subrecord_size = read_int(f, subrecord_offset + 0x02, 4)
        if subrecord_id == Subrecord.NAME.value:
            ils_vor.name = parse_name(f, subrecord_offset, subrecord_size)
        if subrecord_id == Subrecord.ILS_LOCALIZER.value:
            ils_vor.localizer = parse_localizer(f, subrecord_offset, subrecord_size)
        if subrecord_id == Subrecord.DME.value:
            ils_vor.dme = parse_dme(f, subrecord_offset, subrecord_size)
        if subrecord_id == Subrecord.GLIDESLOPE.value:
            ils_vor.glideslope = parse_glideslope(f, subrecord_offset, subrecord_size)
        subrecord_offset += subrecord_size
    return ils_vor


def parse_waypoint(f: BinaryIO, offset: int, size: int) -> Waypoint:
    waypoint = Waypoint(offset, size)
    waypoint.longitude = parse_longitude(f, offset + 0x08, 4)
    waypoint.latitude = parse_latitude(f, offset + 0x0C, 4)
    waypoint.ident = parse_ident(f, offset + 0x14, 4)
    return waypoint


def parse_section(f: BinaryIO, offset: int, _parse_record: Callable) -> List[Any]:
    records = []
    sub_section_size = ((read_int(f, offset + 0x04, 4) & 0x10000) | 0x40000) >> 0x0E
    subsection_count = read_int(f, offset + 0x08, 4)
    first_subsection_offset = read_int(f, offset + 0x0C, 4)
    for y in range(subsection_count):
        subsection_offset = first_subsection_offset + (y * sub_section_size)
        record_count = read_int(f, subsection_offset + 0x04, 4)
        record_offset = read_int(f, subsection_offset + 0x08, 4)
        for z in range(record_count):
            record_size = read_int(f, record_offset + 0x02, 4)
            records.append(_parse_record(f, record_offset, record_size))
            record_offset += record_size
    return records


def parse_bgl(name: str, f: BinaryIO) -> Bgl:
    bgl = Bgl(name)
    bgl.header_size = read_int(f, 0x04, 4)
    bgl.section_count = read_int(f, 0x14, 4)
    for x in range(bgl.section_count):
        section_offset = bgl.header_size + (x * 0x14)
        section_type = read_int(f, section_offset, 4)
        if section_type == Section.AIRPORT.value:
            bgl.airports = parse_section(f, section_offset, parse_airport)
        elif section_type == Section.ILS_VOR.value:
            bgl.ils_vors = parse_section(f, section_offset, parse_ils_vor)
        elif section_type == Section.WAYPOINT.value:
            bgl.waypoints = parse_section(f, section_offset, parse_waypoint)
    return bgl
