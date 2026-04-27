#/usr/bin/python3
import struct
import io
from .properties import PropertyType, Property

class XCFParseError(Exception):
    pass

class Parser():
    """Class that does all the actual work of parsing a character file,
    implements the ContextManager interface to take control of the actual file
    and ensure it is closed even on error"""

    def __init__(self, f):
        if isinstance(f, str):
            self.fname = f
        else:
            self.file = f
            self.fname = None

    #context manager functions
    def __enter__(self):

        #if 'fname' is None it means we were passed an open file
        #and don't need to open a new one
        if self.fname is None:
            return self

        #special case, if fname is '-' use stdin instead
        if self.fname == '-':
            from sys import stdin
            self.file = stdin.buffer
        else:
            self.file = open(self.fname, 'rb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #don't actually close stdin if we're reading from that as we can't open
        #it again
        from sys import stdin
        if self.file is not stdin.buffer:
            self.file.close()

    def properties(self):
        """Returns an iterator over a property block in the file. Assumes the
        file is at a valid point to read properties, if you've just opened the
        file you may need to read_header() first"""

        while True:
            prop = self.read_property()
            if prop is None:
                break
            yield prop

    def read_header(self):
        """reads the file header and returns the number of characters in the
        file"""
        try:
            self.file.seek(0)
        except io.UnsupportedOperation:
            pass

        magic = self.read_int()

        if magic != -1:
            raise XCFParseError("Incorrect Magic Number on file {}: {}".format(self.fname, magic))

        prop = self.read_property()

        # empty files don't have a CharacterPool property
        if prop.name == 'PoolFileName':
            self.expect('None')
            return 0
        elif prop.name != 'CharacterPool':
            raise XCFParseError("Expected Property CharacterPool:ArrayPropery, got {}:{}".format(prop.name, prop.typename))
        count = prop.value

        #I'm not actually convinced this is used, even if it is we're best
        #discarding it and recreating from the actual file name on write
        self.expect('PoolFileName', 'StrProperty')

        self.expect('None')

        _count = self.read_int()

        if count != _count:
            raise XCFParseError("Mismatched character counts: {} != {}".format(count, _count))

        return count

    def expect(self, name, typename = None):
        """read a property expecting it to have name 'name' and type
        'typename', if it doesn't throw an exception"""
        prop = self.read_property()

        #expect a 'None' property
        if name == 'None' and typename is None:
            if prop is not None:
                raise XCFParseError("Expected 'None' Property, got {}:{}".format(prop.name, prop.typename))
            return prop

        try:
            if prop.name != name or prop.typename != typename:
                raise XCFParseError("Expected Property {}:{}, got {}:{}".format(name, typename, prop.name, prop.typename))
        except AttributeError:
            raise XCFParseError("Expected Property {}:{} got {}".format(name, typename, prop))

        return prop

    def read_property(self):
        """read a single property from the file, returns the relevant subtype
        of Property"""
        name = self.read_str()
        self.skip_padding()

        if name == 'None':
            return None

        typename = self.read_str()
        self.skip_padding()

        proptype = PropertyType(typename)

        size = self.read_int()
        self.skip_padding()

        #add a hook to modify size or read extra data if necessary because some properties don't
        #quite follow standard format
        if hasattr(proptype, 'data_read_hook'): 
            size = proptype.data_read_hook(self, size)

        data = self.read(size)
        value = proptype.unpack(data)

        return Property(name, proptype.typename, value)

    def read(self, size):
        buf = self.file.read(size)
        if len(buf) != size:
            raise IOError("Read Error")
        return buf

    def read_int(self):
        return struct.unpack("<i", self.read(4))[0]

    def read_str(self):
        size = self.read_int()
        if size == 0:
            return ''

        bstr = self.read(size)

        #strings should be null terminated
        if bstr[-1] != 0:
            raise XCFParseError("Incorrect String size: {}".format(size))

        return bstr[:-1].decode("latin_1")

    def skip_padding(self):
        pad = self.read_int()
        if pad != 0:
            raise XCFParseError("Expected null padding DWORD, got {}".format(pad))
