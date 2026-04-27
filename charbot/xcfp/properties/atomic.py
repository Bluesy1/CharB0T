#!/usr/bin/python3

import struct
from . import Property, PropertyError

class IntProperty(Property):
    """Integer Property - represented as a little endian DWORD"""

    typename = 'IntProperty'
    expected_type = int

    @classmethod
    def unpack(cls, data):
        return struct.unpack('<i', data)[0]

class ArrayProperty(IntProperty):
    """Array Property - acts as an IntProperty with value of the number of
    elements in the array"""

    typename = 'ArrayProperty'

class BoolProperty(Property):
    """Boolean Property - represented by a single byte, 0x00 is False anything
    else is True"""

    typename = 'BoolProperty'
    expected_type = bool

    @classmethod
    def unpack(cls, data):
        return struct.unpack('?', data)[0]

    #BoolProperty gives incorrect size - should be 1 but shows as 0
    @classmethod
    def data_read_hook(cls, parser, size):
        if size == 0:
            return 1
        return size

class StrProperty(Property):
    """String Property - repersented by a little endian DWORD containing the
    string length followed by a null terminated string - assuming latin-1
    encoding"""

    typename = 'StrProperty'
    expected_type = str

    @classmethod
    def unpack(cls, data):
        size = IntProperty.unpack(data[:4])
        if len(data[4:]) != size:
            raise PropertyError("Incorrect String Size in StrProperty: {}".format(size))
        return data[4:-1].decode("latin_1")

class NameProperty(Property):
    """Name Property - represented as a StrProperty followed by a DWORD that is
    usually (but not always) 0. As the function of this DWORD is unknown for
    the moment we just represent the value of NameProperty as a (str, int)
    tuple"""

    typename = 'NameProperty'
    expected_type = str

    def _set(self, value):
        try:
            (name, param) = value
        except ValueError:
            (name, param) = (value, 0)

        if not isinstance(param, int):
            raise PropertyError(
                    "Tried to set NameProperty.param with non-int type: {}"
                    .format(type(param).__name__)
                )
        super()._set(name)

    @classmethod
    def unpack(cls, data):
        name = StrProperty.unpack(data[:-4])
        val = IntProperty.unpack(data[-4:])
        return (name, val)
