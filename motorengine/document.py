#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.metaclasses import DocumentMetaClass
from motorengine.connection import get_connection, DEFAULT_CONNECTION_NAME


class BaseDocument(object):
    def __init__(self, *args, **kw):
        self._id = None
        for key, value in kw.items():
            if key not in self._db_field_map:
                raise ValueError("Error creating document %s: Invalid property '%s'." % (
                    self.__class__.__name__, key
                ))
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
            callback(instance=self)
        return handle

    def save(self, callback, alias=None):
        document = self.to_dict()
        conn = get_connection()

        coll = conn[self.__collection__]
        coll.insert(document, callback=self.handle_save(callback))

    @classmethod
    def _get_collection_name(cls):
        """Returns the collection name for this class.
        """
        return cls._meta.get('collection', None)

    @classmethod
    def _get_collection(cls):
        """Returns the collection for the document."""
        if not hasattr(cls, '_collection') or cls._collection is None:
            db = cls._get_db()
            collection_name = cls._get_collection_name()

            cls._collection = db[collection_name]

        return cls._collection

    @classmethod
    def _get_db(cls):
        """Some Model using other db_alias"""
        return get_connection(alias=cls._meta.get("db_alias", DEFAULT_CONNECTION_NAME))

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            return self._fields[name].get_value()

        return object.__getattribute__(self, name)


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    my_metaclass = DocumentMetaClass
