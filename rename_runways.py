from __future__ import annotations
import csv
import os.path
import shutil
import sys
from collections import defaultdict
from pathlib import Path

from lib import *

MSFS_ROOT = Path('G:/MSFS/Microsoft Flight Simulator')
BACKUP_DIR = Path('backup')
TEST_MODE = False

sys.argv.pop(0)
while sys.argv:
    arg = sys.argv.pop(0)
    if arg == '-x':
        TEST_MODE = True
    elif arg == '-r':
        MSFS_ROOT = Path(sys.argv.pop(0))
    elif arg == '-b':
        b = sys.argv.pop(0)
        if b == '':
            BACKUP_DIR = None
        else:
            BACKUP_DIR = Path(sys.argv.pop(0))
    else:
        raise Exception('Unknown arg ' + arg)


class RunwayChange:
    bgl: Path
    airport: str
    oldRunwayNumber: str
    oldRunwayDesignator: str
    newRunwayNumber: str
    newRunwayDesignator: str

    def __init__(self, bgl: Path, airport: str, old_runway_number: str, old_runway_designator: str,
                 new_runway_number: str, new_runway_designator: str) -> None:
        self.bgl = bgl
        self.airport = airport
        self.oldRunwayNumber = old_runway_number
        self.oldRunwayDesignator = old_runway_designator
        self.newRunwayNumber = new_runway_number
        self.newRunwayDesignator = new_runway_designator


designators = ['L', 'R', 'C', 'W', 'A', 'B']
special_numbers = ['n', 'ne', 'e', 'se', 's', 'sw', 'n', 'w', 'nw']


def split_number_and_designator(value: str):
    number = value.strip()
    designator = ''
    if number[-1] in designators:
        designator = number[-1]
        number = number[:-1]
    if number.isnumeric():
        n = int(number)
        if 1 <= n <= 36:
            return number, designator
    if number in special_numbers:
        return number, designator
    raise Exception('Invalid runway number:', value)


def get_airport(bgl: Bgl, ident: str) -> Optional[Airport]:
    for airport in bgl.airports:
        if airport.ident.val == ident:
            return airport
    return None


def do_change(f: BinaryIO, airport: Airport, change: RunwayChange):
    msg = ('Update ' + airport.ident.val + ' [' + change.oldRunwayNumber + change.oldRunwayDesignator + '] -> [' +
           change.newRunwayNumber + change.newRunwayDesignator + ']\t-- ')

    runway_updates = 0
    start_updates = 0
    taxiway_updates = 0
    for runway in airport.runways:
        if (runway.primary_number.display == change.oldRunwayNumber
                and runway.primary_designation.display == change.oldRunwayDesignator):
            new_bytes = from_int(runway_number_to_int(change.newRunwayNumber), runway.primary_number.size)
            f.seek(runway.primary_number.offset)
            if not TEST_MODE:
                f.write(new_bytes)
            new_bytes = from_int(runway_designator_to_int(change.newRunwayDesignator),
                                 runway.primary_designation.size)
            f.seek(runway.primary_designation.offset)
            if not TEST_MODE:
                f.write(new_bytes)
            runway_updates += 1

        if (runway.secondary_number.display == change.oldRunwayNumber
                and runway.secondary_designation.display == change.oldRunwayDesignator):
            new_bytes = from_int(runway_number_to_int(change.newRunwayNumber), runway.secondary_number.size)
            f.seek(runway.secondary_number.offset)
            if not TEST_MODE:
                f.write(new_bytes)
            new_bytes = from_int(runway_designator_to_int(change.newRunwayDesignator),
                                 runway.secondary_designation.size)
            f.seek(runway.secondary_designation.offset)
            if not TEST_MODE:
                f.write(new_bytes)
            runway_updates += 1

    for start in airport.starts:
        if (start.type.val == StartType.RUNWAY.value and start.number.display == change.oldRunwayNumber
                and start.designator.display == change.oldRunwayDesignator):
            if start.designator.size != 1:
                raise Exception(start)

            new_bytes = from_int(runway_number_to_int(change.newRunwayNumber), start.number.size)
            f.seek(start.number.offset)
            if not TEST_MODE:
                f.write(new_bytes)

            f.seek(start.designator.offset)
            old_bytes = f.read(start.designator.size)
            new_bytes = from_int(runway_designator_to_int(change.newRunwayDesignator), start.designator.size)
            combined = from_int(((old_bytes[0] >> 4) << 4) + new_bytes[0], start.designator.size)
            f.seek(start.designator.offset)
            if not TEST_MODE:
                f.write(combined)
            start_updates += 1

    for taxiway_path in airport.taxiwayPaths:
        if (taxiway_path.type.val == 2 and taxiway_path.number.display == change.oldRunwayNumber
                and taxiway_path.designator.display == change.oldRunwayDesignator):
            if taxiway_path.designator.size != 1:
                raise Exception(taxiway_path)

            new_bytes = from_int(runway_number_to_int(change.newRunwayNumber), taxiway_path.number.size)
            f.seek(taxiway_path.number.offset)
            if not TEST_MODE:
                f.write(new_bytes)

            f.seek(taxiway_path.designator.offset)
            old_bytes = f.read(taxiway_path.designator.size)
            new_bytes = from_int(runway_designator_to_int(change.newRunwayDesignator),
                                 taxiway_path.designator.size)
            combined = from_int((old_bytes[0] & 0b00001111) + (new_bytes[0] << 4), taxiway_path.designator.size)
            f.seek(taxiway_path.designator.offset)
            if not TEST_MODE:
                f.write(combined)
            taxiway_updates += 1

    if runway_updates == 0 and start_updates == 0 and taxiway_updates == 0:
        msg += 'Runway [' + change.oldRunwayNumber + change.oldRunwayDesignator + '] not found!'
    else:
        msg += 'runways=' + str(runway_updates) + ' starts=' + str(start_updates) + ' taxiways=' + str(taxiway_updates)
    print(msg)


def main():
    if TEST_MODE:
        print('!! TEST MODE !!')
    if not MSFS_ROOT.exists():
        if input('MSFS root not found, backup disabled. Continue? (y)') != 'y':
            return
    else:
        if BACKUP_DIR is None:
            print('Backup disabled.')
        elif BACKUP_DIR.is_relative_to(MSFS_ROOT):
            raise Exception('Backup directory must not be inside MSFS root.')

    runway_changes: dict[Path, dict[str, list[RunwayChange]]] = defaultdict(lambda: defaultdict(list))
    with open('runways.csv', 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=';')
        rows = [row for row in reader]
        for row in rows:
            if len(row) == 4:
                old_number, old_designator = split_number_and_designator(row[2])
                new_number, new_designator = split_number_and_designator(row[3])
                runway_change = RunwayChange(Path(row[0].replace('<msfs>', str(MSFS_ROOT))), row[1], old_number,
                                             old_designator, new_number, new_designator)
                runway_changes[runway_change.bgl][runway_change.airport].append(runway_change)
            else:
                raise Exception('Malformed row:', row)

    for bgl_file in runway_changes:
        print(bgl_file)
        if not bgl_file.exists():
            print('WARN: File not found:', bgl_file)
            continue
        if MSFS_ROOT.exists() and BACKUP_DIR is not None and bgl_file.is_relative_to(MSFS_ROOT):
            bak = BACKUP_DIR.joinpath(bgl_file.relative_to(MSFS_ROOT))
            if not TEST_MODE and not bak.exists():
                os.makedirs(bak.parent, exist_ok=True)
                shutil.copyfile(bgl_file, bak)
        mode = 'rb+'
        if TEST_MODE:
            mode = 'rb'
        with open(bgl_file, mode) as f:
            bgl = parse_bgl(str(bgl_file), f)
            for change_airport in runway_changes[bgl_file]:
                airport = get_airport(bgl, change_airport)
                if airport is None:
                    print('WARN: Airport', change_airport, 'not in BGL file.')
                    continue
                changes = runway_changes[bgl_file][change_airport]
                for change in changes:
                    do_change(f, airport, change)


if __name__ == "__main__":
    main()
