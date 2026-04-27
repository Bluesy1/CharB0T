#!/usr/bin/python
from collections import OrderedDict

from . import PropertyType, Property
from ..property_set import PropertySet, PropertySetMeta

# As a class can only have 1 metaclass and StructPropertys inherit from 2 classes
# that each have their own metaclass we need to resolve this conflict. As it
# happens both PropertyType and PropertySetMeta are friendly enough that we
# could make one a subclass of the other and they would do the right thing when
# used with classes that only inherit from one of Property or PropertySet,
# however I feel this would couple two insuffiently related classes so instead
# we're going to give Structs their own metaclass that inherits from both and
# let super() do the work of properly delegating __new__.
class StructMeta(PropertySetMeta, PropertyType):
    """StructProperty metaclass"""
    def __new__(cls, name, bases, namespace, **kwargs):
        return super().__new__(cls, name, bases, namespace, **kwargs)

class StructProperty(Property, PropertySet, metaclass=StructMeta):
    """Struct Property - a struct represented as a sequence of properties ended
    with 'None'"""

    typename = 'StructProperty'

    def __init__(self, name, typename, properties=None, **kwargs):
        self.name = name
        PropertySet.__init__(self, properties, **kwargs)

    def _get(self):
        return self

    @classmethod
    def unpack(cls, data):
        from ..parser import Parser
        import io
        return Parser(io.BytesIO(data)).properties()

    def __str__(self):
        return "<struct: {}>".format(self.typename)

    @classmethod
    def data_read_hook(cls, parser, size):
        cls.typename = parser.read_str()
        parser.skip_padding()

        return size

class AppearanceStruct(StructProperty):
    """represents a TAppearance struct in a character file"""

    typename = 'TAppearance'

    #defaults taken from Ana Ramirez from the Demos&Replays.bin file that
    #comes with the game
    head   = Property('nmHead',  'NameProperty','LatFem_C')
    gender = Property('iGender', 'IntProperty', 2)
    race   = Property('iRace',   'IntProperty', 3)

    haircut    = Property('nmHaircut',   'NameProperty', 'Female_LongWavy')
    hairColor  = Property('iHairColor',  'IntProperty', 0)
    facialHair = Property('iFacialHair', 'IntProperty', 0)
    beard      = Property('nmBeard',     'NameProperty', 'None')

    skinColor = Property('iSkinColor', 'IntProperty', 5)
    eyeColor  = Property('iEyeColor',  'IntProperty', 15)

    flag = Property('nmFlag', 'NameProperty', 'Country_Mexico')

    iVoice   = Property('iVoice', 'IntProperty', 14)
    attitude = Property('iAttitude', 'IntProperty', 0)

    armorDecoration    = Property('iArmorDeco', 'IntProperty', -1)
    armorTint          = Property('iArmorTint', 'IntProperty', 31)
    armorTintSecondary = Property('iArmorTintSecondary', 'IntProperty', 10)
    weaponTint         = Property('iWeaponTint', 'IntProperty', -1)
    tattooTint         = Property('iTattooTint', 'IntProperty', -1)

    weaponPattern = Property('nmWeaponPattern', 'NameProperty', 'Pat_Nothing')

    pawn = Property('nmPawn', 'NameProperty', 'None')

    torse  = Property('nmTorso',  'NameProperty', 'CnvMed_Std_C_F')
    arms   = Property('nmArms',   'NameProperty', 'CnvMed_Std_F_F')
    legs   = Property('nmLegs',   'NameProperty', 'CnvMed_Std_C_F')
    helmet = Property('nmHelmet', 'NameProperty', 'Helmet_0_NoHelmet_F')
    eyes   = Property('nmEye',    'NameProperty', ('DefaultEyes', 3))
    teeth  = Property('nmTeeth',  'NameProperty', 'DefaultTeeth')

    propLower = Property('nmFacePropLower', 'NameProperty', 'Prop_FaceLower_Blank',)
    propUpper = Property('nmFacePropUpper', 'NameProperty', 'None')

    patterns = Property('nmPatterns', 'NameProperty', 'Pat_Nothing')

    nmVoice  = Property('nmVoice', 'NameProperty', 'FemaleVoice1_English_US')
    language = Property('nmLanguage', 'NameProperty', 'None')

    leftTattoo  = Property('nmTattoo_LeftArm',  'NameProperty', 'Tattoo_Arms_BLANK')
    rightTattoo = Property('nmTattoo_RightArm', 'NameProperty', 'Tattoo_Arms_BLANK')
    scars       = Property('nmScars', 'NameProperty', 'Scars_BLANK')

    torsoUnderlay = Property('nmTorsoUnderlay', 'NameProperty', 'CnvUnderlay_std_A_F')
    armsUnderlay  = Property('nmArmsUnderlay',  'NameProperty', 'CnvMed_Underlay_A_F')
    legsUnderlay  = Property('nmLegsUnderlay',  'NameProperty', 'CnvUnderlay_std_A_F')
