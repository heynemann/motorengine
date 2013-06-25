#!/usr/bin/env python
# -*- coding: utf-8 -*-


from motorengine.connection import get_connection


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass

    def coll(self, alias):
        if alias is not None:
            conn = get_connection(alias=alias)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

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
