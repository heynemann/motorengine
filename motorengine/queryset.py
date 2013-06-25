#!/usr/bin/env python
# -*- coding: utf-8 -*-


from motorengine.connection import get_connection


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = None

    def coll(self, alias):
        if alias is not None:
            conn = get_connection(alias=alias)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

    def create(self, callback, alias=None, **kwargs):
        document = self.__klass__(**kwargs)
        self.save(document=document, callback=callback, alias=alias)

    def save(self, document, callback, alias=None):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))
        doc = document.to_dict()
        self.coll(alias).insert(doc, callback=callback)

    def handle_get(self, callback):
        def handle(*args, **kw):
            instance = args[0]
            callback(instance=self.__klass__.from_dict(instance))

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

    def handle_find_all(self, callback):
        def handle(*arguments, **kwargs):
            result = []
            for doc in arguments[0]:
                result.append(self.__klass__.from_dict(doc))

            callback(result=result)

        return handle

    def find_all(self, callback, alias=None):
        arguments = dict(callback=self.handle_find_all(callback))
        if self._limit is not None:
            arguments['length'] = self._limit
        self.coll(alias).find(self._filters).to_list(**arguments)
