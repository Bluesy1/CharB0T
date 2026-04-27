from .character import Character
from .parser import Parser

class CharacterPool():
    
    def __init__(self, fname):
        self.fname = fname


    def characters(self):
        """returns an iterator for the characters in this file"""

        with Parser(self.fname) as parser:
            count = parser.read_header()

            for _ in range(count):
                char = Character()
                char.add_properties(parser.properties())
                yield char
