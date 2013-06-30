#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.metaclasses import DocumentMetaClass
from motorengine.errors import InvalidDocumentError
from motorengine.utils import get_class


AUTHORIZED_FIELDS = ['_id', '_values']


class BaseDocument(object):
    def __init__(self, *args, **kw):
        self._id = kw.pop('_id', None)
        self._values = {}

        for key, field in self._fields.items():
            self._values[key] = field.default

        for key, value in kw.items():
            if key not in self._db_field_map:
                raise ValueError("Error creating document %s: Invalid property '%s'." % (
                    self.__class__.__name__, key
                ))
            self._values[key] = value

    @classmethod
    def from_son(cls, dic):
        klass = get_class(dic.pop('__module__'), dic.pop('__class__'))

        field_values = {}
        for name, value in dic.items():
            if name in cls._fields:
                field_values[name] = cls._fields[name].from_son(value)
            else:
                field_values[name] = value

        return klass(**field_values)

    def to_son(self):
        data = {
            "__module__": self.__module__,
            "__class__": self.__class__.__name__
        }

        for name, value in self._values.items():
            data[name] = self._fields[name].to_son(value)
        return data

    def validate_fields(self):
        for name, field in self._fields.items():
            if field.required and field.is_empty(self._values[field.db_field]):
                raise InvalidDocumentError("Field '%s' is required." % name)

        return True

    def handle_save(self, callback):
        def handle(*args, **kw):
            # error?
            if len(args) > 1 and args[1]:
                raise args[1]

            self._id = args[0]
            callback(instance=self)
        return handle

    def save(self, callback, alias=None):
        if self.validate_fields():
            self.objects.save(self, callback=self.handle_save(callback), alias=alias)

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            return self._values.get(name, None)

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name not in AUTHORIZED_FIELDS and name not in self._fields:
            raise ValueError("Error updating property: Invalid property '%s'." % name)

        if name in self._fields:
            self._values[name] = value
            return

        object.__setattr__(self, name, value)


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    pass
