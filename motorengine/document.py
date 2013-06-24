#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.metaclasses import DocumentMetaClass
from motorengine.connection import get_connection


AUTHORIZED_FIELDS = ['_id']


class BaseDocument(object):
    def __init__(self, *args, **kw):
        self._id = None
        for key, value in kw.items():
            if key not in self._db_field_map:
                raise ValueError("Error creating document %s: Invalid property '%s'." % (
                    self.__class__.__name__, key
                ))
            self._fields[key].set_value(value)

    def to_dict(self):
        data = {}
        for name, field in self._fields.items():
            data[name] = field.to_dict()
        return data

    def handle_save(self, callback):
        def handle(*args, **kw):
            # error?
            if len(args) > 1 and args[1]:
                raise args[1]

            self._id = args[0]
            callback(instance=self)
        return handle

    def save(self, callback, alias=None):
        document = self.to_dict()
        conn = get_connection()

        coll = conn[self.__collection__]
        coll.insert(document, callback=self.handle_save(callback))

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            return self._fields[name].get_value()

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name not in AUTHORIZED_FIELDS and name not in self._fields:
            raise ValueError("Can't set a property for an unknown field: %s" % name)

        if name in AUTHORIZED_FIELDS:
            object.__setattr__(self, name, value)
            return

        self._fields[name].set_value(value)


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    pass
