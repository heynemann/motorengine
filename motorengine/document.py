#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.metaclasses import DocumentMetaClass
from motorengine.connection import get_connection


class BaseDocument(object):
    def __init__(self, *args, **kw):
        self._id = None
        for key, value in kw.items():
            if key not in self._db_field_map:
                continue
            self._fields[key].value = value

    def to_dict(self):
        data = {}
        for name, field in self._fields.items():
            data[name] = field.to_dict()
        return data

    def handle_save(self, callback):
        def handle(*args, **kw):
            if len(args) > 1 and args[1]:
                raise args[1]
            self._id = args[0]
            callback(self)
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


class Document(BaseDocument, metaclass=DocumentMetaClass):
    __metaclass__ = DocumentMetaClass
