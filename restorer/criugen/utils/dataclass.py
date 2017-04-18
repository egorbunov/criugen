# coding: utf-8

"""
Simple immutable data classes in python
"""


import itertools
import collections
import warnings


def iterate(fun, init):
    while True:
        yield init
        init = fun(init)


class FieldNotInitialized(Exception):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        return "You forgot to initialize {} field".format(repr(self.field_name))


class UnknownFieldsSpecified(Exception):
    def __init__(self, fields):
        self.unk_fields = list(fields)

    def __str__(self):
        return "Unknown fields passed: {}".format(repr(self.unk_fields))


class ImmutableFieldChange(Exception):
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
    def __hooked_init(self, **kwargs):
        """Method, which is called during instance creation

        Ensures, that all fields are initialized
        """
        for field in self.__slots__:
            if field not in kwargs:
                raise FieldNotInitialized(field)
            setattr(self, field, kwargs[field])

        if len(kwargs) != len(self.__slots__):
            raise UnknownFieldsSpecified(set(kwargs) - set(self.__slots__))

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
            def getbase(cls):
                return cls.__bases__[0]

            # choosing highest parent with DataClassMeta metaclass
            # TODO: think about proper delegation
            setattr_delegat = next(c for c in iterate(getbase, type(self))
                                   if not hasattr(getbase(c), '__metaclass__')
                                   or getbase(c).__metaclass__ != DataClassMeta)

            super(setattr_delegat, self).__setattr__(field, value)
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
