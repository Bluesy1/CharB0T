#!/usr/bin/python3
from collections import OrderedDict
from .properties import Property

class PropertySetMeta(type):
    """Metaclass for PropertySets
    Responsible for creating an OrderedDict called field_names which defines
    the order fields should be stored to file and allows mapping from python
    attribute names to property names"""

    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return OrderedDict()

    def __new__(cls, name, bases, namespace, **kwargs):
        result = super().__new__(cls, name, bases, dict(namespace))
        result.field_names = OrderedDict()
        for name, value in namespace.items():
            if not isinstance(value, Property):
                continue
            result.field_names[name] = value.name
        return result

class PropertySet(metaclass=PropertySetMeta):
    """Base class for classes that consist of a set of named properties"""

    def __init__(self, properties=None, **kwargs):
        self.fields = {}
        if properties is not None:
            self.add_properties(properties)

        for key,value in kwargs.items():
            if key in self.field_names:
                setattr(self, key, value)

    def add_property(self, property):
        self.fields[property.name] = property
        

    def add_properties(self, iter):
        for property in iter:
            self.add_property(property)
