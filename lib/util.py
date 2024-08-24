import struct
from typing import BinaryIO, Any, NoReturn


def is_blank(val: str) -> bool:
    return not (val and val.strip())


def is_not_blank(val: str) -> bool:
    return bool(val and val.strip())


def prnt(name: str, value: Any, indent: int = 0) -> NoReturn:
    print(('\t' * indent) + name + ': ' + str(value))


def decode_ident(ident_value: int, shift: bool = True) -> str:
    calc = ident_value
    res = ''
    if calc != 0:
        if shift:
            calc >>= 5
        while calc >= 38:
            p = calc % 38
            res = get_ident_char(p) + res
            calc = (calc - p) // 38
        res = get_ident_char(calc) + res
    return res


def runway_number_to_int(number: str) -> int:
    if number == 'n':
        return 37
    elif number == 'ne':
        return 38
    elif number == 'e':
        return 39
    elif number == 'se':
        return 40
    elif number == 's':
        return 41
    elif number == 'sw':
        return 42
    elif number == 'w':
        return 43
    elif number == 'nw':
        return 44
    else:
        n = int(number)
        if n < 1 or n > 36:
            raise Exception(number)
        return n


def runway_designator_to_int(designator: str) -> int:
    if designator == '':
        return 0
    elif designator == 'L':
        return 1
    elif designator == 'R':
        return 2
    elif designator == 'C':
        return 3
    elif designator == 'W':
        return 4
    elif designator == 'A':
        return 5
    elif designator == 'B':
        return 6
    raise Exception(designator)


def get_ident_char(char_value: int) -> str:
    if char_value == 0:
        return ' '
    elif 2 <= char_value <= 11:
        return chr(char_value + 46)
    elif 12 <= char_value <= 37:
        return chr(char_value + 53)
    else:
        raise Exception('Character value [' + str(char_value) + '] not valid.')


def read(file: BinaryIO, offset: int, size: int) -> bytes:
    file.seek(offset)
    return file.read(size)


def read_int(file: BinaryIO, offset: int, size: int) -> int:
    return int.from_bytes(read(file, offset, size), byteorder='little', signed=False)


def read_float(file: BinaryIO, offset: int, size: int) -> float:
    return struct.unpack('<f', read(file, offset, size))[0]


def to_int(barr: bytes) -> int:
    return int.from_bytes(barr, byteorder='little', signed=False)


def from_int(i: int, size: int) -> bytes:
    return i.to_bytes(size, 'little')


def to_float(barr: bytes) -> float:
    return struct.unpack('<f', barr)[0]


def to_string(barr: bytes, encoding: str = 'ascii') -> str:
    return barr.decode(encoding=encoding).rstrip('\x00')


def from_float(flt: float) -> bytes:
    return struct.pack('<f', flt)
