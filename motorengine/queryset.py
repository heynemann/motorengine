#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine import ASCENDING
from motorengine.connection import get_connection


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = 300
        self._order_fields = []

    @property
    def is_lazy(self):
        return self.__klass__.__lazy__

    def coll(self, alias):
        if alias is not None:
            conn = get_connection(alias=alias)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

    def create(self, callback, alias=None, **kwargs):
        document = self.__klass__(**kwargs)
        self.save(document=document, callback=callback, alias=alias)

    def handle_save(self, document, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            document._id = arguments[0]
            callback(instance=document)

        return handle

    def save(self, document, callback, alias=None):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))
        doc = document.to_son()
        self.coll(alias).insert(doc, callback=self.handle_save(document, callback))

    def handle_auto_load_references(self, doc, callback):
        def handle(*args, **kw):
            if 'result' in kw:
                callback(instance=doc)
                return

            callback(instance=None)

        return handle

    def handle_get(self, callback):
        def handle(*args, **kw):
            instance = args[0]

            if instance is None:
                callback(instance=None)
            else:
                doc = self.__klass__.from_son(instance)
                if self.is_lazy:
                    callback(instance=doc)
                else:
                    doc.load_references(callback=self.handle_auto_load_references(doc, callback))

        return handle

    def get(self, id, callback, alias=None):
        self.coll(alias).find_one({
            "_id": id
        }, callback=self.handle_get(callback))

    def filter(self, **kwargs):
        for field_name, value in kwargs.items():
            if field_name not in self.__klass__._fields:
                raise ValueError("Invalid filter '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))
            field = self.__klass__._fields[field_name]
            self._filters[field.db_field] = field.to_son(value)
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def order_by(self, field_name, direction=ASCENDING):
        if field_name not in self.__klass__._fields:
            raise ValueError("Invalid order by field '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))

        field = self.__klass__._fields[field_name]
        self._order_fields.append((field.db_field, direction))
        return self

    def handle_find_all(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            result = []
            for doc in arguments[0]:
                result.append(self.__klass__.from_son(doc))

            callback(result=result)

        return handle

    def _get_find_cursor(self, alias):
        find_arguments = {}

        if self._order_fields:
            find_arguments['sort'] = self._order_fields

        return self.coll(alias).find(self._filters, **find_arguments)

    def find_all(self, callback, alias=None):
        to_list_arguments = dict(callback=self.handle_find_all(callback))

        if self._limit is not None:
            to_list_arguments['length'] = self._limit

        self._get_find_cursor(alias=alias).to_list(**to_list_arguments)

    def handle_count(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]
            callback(result=arguments[0])

        return handle

    def count(self, callback, alias=None):
        self._get_find_cursor(alias=alias).count(callback=self.handle_count(callback))
