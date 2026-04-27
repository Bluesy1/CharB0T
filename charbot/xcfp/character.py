from .properties import Property
from .property_set import PropertySet

class Character(PropertySet):
    """Represents an XCOM 2 character in a character pool file"""

    # template for per instance field OrederedDicts
    firstName = Property('strFirstName', 'StrProperty', '')
    lastName  = Property('strLastName', 'StrProperty', '')
    nickName  = Property('strNickName', 'StrProperty', '')

    soldierClass = Property('m_SoldierClassTemplateName', 'NameProperty', 'Rookie')
    characterTemplate = Property('CharacterTemplateName', 'NameProperty', 'Soldier')

    appearance = Property('kAppearance', 'TAppearance')

    country = Property('Country', 'NameProperty', 'Country_UK')

    allowedTypeSoldier = Property('AllowedTypeSoldier', 'BoolProperty', True)
    allowedTypeVIP     = Property('AllowedTypeVIP',     'BoolProperty', True)
    allowedTypeDarkVIP = Property('AllowedTypeDarkVIP', 'BoolProperty', True)

    timestamp = Property('PoolTimestamp', 'StrProperty', '')
    biography = Property('BackgroundText', 'StrProperty', '')

    def __str__(self):
        fields = filter(None, (self.firstName, self.nickName, self.lastName))
        return ' '.join(fields)

    def details(self):
        result = ""
        for name in self.field_names.keys():
            result += "{}: {}\n".format(name, getattr(self, name))

        return result
