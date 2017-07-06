# coding: utf-8

"""
Simple immutable data classes in python
"""

import collections
import itertools
import warnings


def iterate(fun, init):
    while True:
        yield init
        init = fun(init)


class FieldsNotInitialized(Exception):
    def __init__(self, fields):
        self.fields = fields

    def __str__(self):
        return "You forgot to initialize {} fields".format(repr(self.fields))


class UnknownFieldSpecified(Exception):
    def __init__(self, field):
        self.field = list(field)

    def __str__(self):
        return "Unknown fields passed: {}".format(repr(self.field))


class ImmutableFieldChange(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Can't change immutable field: {}".format(repr(self.field))


class BadInitArgument(Exception):
    def __str__(self):
        return "Bad constructor argument: it's either not base type instance or base type instance duplicate"


class DuplicateFieldInit(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Can't change immutable field: {}".format(repr(self.field))


class DataClassMeta(type):
    @staticmethod
    def __pop_field_names(attrs):
        """
        Pops out attributes, which does't look like user-defined fields, to
        the list
        """
        filed_names = [k for k in attrs if not k.startswith("_")]

        for f in filed_names:
            val = attrs.pop(f)
            if type(val) != str:
                warnings.warn("It is better to initialize fields with doc comment =)")

        return filed_names

    @staticmethod
    def __hooked_init(self, *args, **kwargs):
        """Method, which is called during instance creation

        Ensures, that all fields are initialized
        
        The data class can be initiated with keyword arguments or with
        arguments, which must be instances of parent data classes (bases)
        """
        bases = set(type(self).__bases__)
        for a in args:
            if type(a) not in bases:
                raise BadInitArgument()
            bases.remove(type(a))
            for field in a.__slots__:
                setattr(self, field, getattr(a, field))

        for field in kwargs:
            if hasattr(self, field):
                raise DuplicateFieldInit(field)
            if field not in self.__slots__:
                raise UnknownFieldSpecified(field)

            setattr(self, field, kwargs[field])

        not_initialized_fields = [field for field in self.__slots__ if not hasattr(self, field)]
        if not_initialized_fields:
            raise FieldsNotInitialized(not_initialized_fields)

    @staticmethod
    def __hooked_repr(self):
        return "{}({})".format(
            type(self).__name__,
            ", ".join(["{}={}".format(k, getattr(self, k)) for k in self.__slots__])
        )

    @staticmethod
    def __hooked_setattr(self, field, value):
        """
        Ensures, that user can't mutate object after initialization
        """

        if not hasattr(self, field):
            object.__setattr__(self, field, value)
        else:
            raise ImmutableFieldChange(field)

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        # only python 3
        return collections.OrderedDict()

    def __new__(mcs, name, bases, attrs, **kwargs):
        field_names = list(itertools.chain(
            DataClassMeta.__pop_field_names(attrs),
            *[getattr(b, '__slots__') if hasattr(b, '__slots__') else [] for b in bases]
        ))

        attrs['__slots__'] = field_names
        attrs['__init__'] = DataClassMeta.__hooked_init
        attrs['__repr__'] = DataClassMeta.__hooked_repr
        attrs['__setattr__'] = DataClassMeta.__hooked_setattr

        return super(DataClassMeta, mcs).__new__(mcs, name, bases, attrs)


class DataClass(object):
    __metaclass__ = DataClassMeta
