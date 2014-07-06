#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from pymongo.errors import DuplicateKeyError
from tornado.concurrent import return_future
from easydict import EasyDict as edict
from bson.objectid import ObjectId

from motorengine import ASCENDING
from motorengine.aggregation.base import Aggregation
from motorengine.connection import get_connection
from motorengine.errors import UniqueKeyViolationError

DEFAULT_LIMIT = 1000

class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = None
        self._skip = None
        self._order_fields = []

    @property
    def is_lazy(self):
        return self.__klass__.__lazy__

    def coll(self, alias=None):
        if alias is not None:
            conn = get_connection(alias=alias)
        elif self.__klass__.__alias__ is not None:
            conn = get_connection(alias=self.__klass__.__alias__)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

    @return_future
    def create(self, callback, alias=None, **kwargs):
        '''
        Creates and saved a new instance of the document.

        .. testsetup:: saving_create

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserCreatingInstances"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_create

            def handle_user_created(user):
                try:
                    assert user.name == "Bernardo"
                finally:
                    io_loop.stop()

            def create_user():
                User.objects.create(name="Bernardo", callback=handle_user_created)

            io_loop.add_timeout(1, create_user)
            io_loop.start()
        '''
        document = self.__klass__(**kwargs)
        self.save(document=document, callback=callback, alias=alias)

    def handle_save(self, document, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                if isinstance(arguments[1], (DuplicateKeyError, )):
                    raise UniqueKeyViolationError.from_pymongo(str(arguments[1]), self.__klass__)
                else:
                    raise arguments[1]

            document._id = arguments[0]
            callback(document)

        return handle

    def handle_update(self, document, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            callback(document)

        return handle

    def update_field_on_save_values(self, document, creating):
        for field_name, field in self.__klass__._fields.items():
            if field.on_save is not None:
                setattr(document, field_name, field.on_save(document, creating))

    def save(self, document, callback, alias=None):
        if self.validate_document(document):
            self.ensure_index(callback=self.indexes_saved_before_save(document, callback, alias))

    def indexes_saved_before_save(self, document, callback, alias):
        def handle(*args, **kw):
            self.update_field_on_save_values(document, document._id is not None)
            doc = document.to_son()

            if document._id is not None:
                self.coll(alias).update({'_id': document._id}, doc, callback=self.handle_update(document, callback))
            else:
                self.coll(alias).insert(doc, callback=self.handle_save(document, callback))

        return handle

    def validate_document(self, document):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))

        return document.validate()

    def handle_bulk_insert(self, documents, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            for object_index, object_id in enumerate(arguments[0]):
                documents[object_index]._id = object_id
            callback(documents)

        return handle

    @return_future
    def bulk_insert(self, documents, callback=None, alias=None):
        '''
        Inserts all documents passed to this method in one go.
        '''

        is_valid = True
        docs_to_insert = []

        for document_index, document in enumerate(documents):
            try:
                is_valid = is_valid and self.validate_document(document)
            except Exception:
                err = sys.exc_info()[1]
                raise ValueError("Validation for document %d in the documents you are saving failed with: %s" % (
                    document_index,
                    str(err)
                ))

            if not is_valid:
                return

            docs_to_insert.append(document.to_son())

        if not is_valid:
            return

        self.coll(alias).insert(docs_to_insert, callback=self.handle_bulk_insert(documents, callback))

    def handle_update_documents(self, callback):
        def handle(*arguments, **kwargs):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            callback(edict({
                "count": int(arguments[0]['n']),
                "updated_existing": arguments[0]['updatedExisting']
            }))

        return handle

    def transform_definition(self, definition):
        from motorengine.fields.base_field import BaseField

        result = {}

        for key, value in definition.items():
            if isinstance(key, (BaseField, )):
                result[key.db_field] = value
            else:
                result[key] = value

        return result

    @return_future
    def update(self, definition, callback=None, alias=None):
        if callback is None:
            raise RuntimeError("The callback argument is required")

        definition = self.transform_definition(definition)

        update_filters = {}
        if self._filters:
            update_filters = self.get_query_from_filters(self._filters)

        update_arguments = dict(
            spec=update_filters,
            document={'$set': definition},
            multi=True,
            callback=self.handle_update_documents(callback)
        )
        self.coll(alias).update(**update_arguments)

    @return_future
    def delete(self, callback=None, alias=None):
        '''
        Removes all instances of this document that match the specified filters (if any).

        .. testsetup:: saving_delete

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstances"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete

            def handle_user_created(user):
                User.objects.filter(name="Bernardo").delete(callback=handle_users_deleted)

            def handle_users_deleted(number_of_deleted_items):
                try:
                    assert number_of_deleted_items == 1
                finally:
                    io_loop.stop()

            def create_user():
                user = User(name="Bernardo")
                user.save(callback=handle_user_created)

            io_loop.add_timeout(1, create_user)
            io_loop.start()
        '''

        self.remove(callback=callback, alias=alias)

    def handle_remove(self, callback):
        def handle(*args, **kw):
            callback(args[0]['n'])

        return handle

    def remove(self, instance=None, callback=None, alias=None):
        if callback is None:
            raise RuntimeError("The callback argument is required")

        if instance is not None:
            if hasattr(instance, '_id') and instance._id:
                self.coll(alias).remove(instance._id, callback=self.handle_remove(callback))
        else:
            if self._filters:
                remove_filters = self.get_query_from_filters(self._filters)
                self.coll(alias).remove(remove_filters, callback=self.handle_remove(callback))
            else:
                self.coll(alias).remove(callback=self.handle_remove(callback))

    def handle_auto_load_references(self, doc, callback):
        def handle(*args, **kw):
            if len(args) > 0:
                callback(doc)
                return

            callback(None)

        return handle

    def handle_get(self, callback):
        def handle(*args, **kw):
            instance = args[0]

            if instance is None:
                callback(None)
            else:
                doc = self.__klass__.from_son(instance)
                if self.is_lazy:
                    callback(doc)
                else:
                    doc.load_references(callback=self.handle_auto_load_references(doc, callback))

        return handle

    @return_future
    def get(self, id=None, callback=None, alias=None, **kwargs):
        '''
        Gets a single item of the current queryset collection using it's id.

        In order to query a different database, please specify the `alias` of the database to query.
        '''

        from motorengine import Q

        if id is None and not kwargs:
            raise RuntimeError("Either an id or a filter must be provided to get")

        if id is not None:
            if not isinstance(id, ObjectId):
                id = ObjectId(id)

            filters = {
                "_id": id
            }
        else:
            filters = Q(**kwargs)
            filters = self.get_query_from_filters(filters)

        self.coll(alias).find_one(filters, callback=self.handle_get(callback))

    def get_query_from_filters(self, filters):
        if not filters:
            return {}

        query = filters.to_query(self.__klass__)
        return query

    def _get_find_cursor(self, alias):
        find_arguments = {}

        if self._order_fields:
            find_arguments['sort'] = self._order_fields

        if self._limit:
            find_arguments['limit'] = self._limit

        if self._skip:
            find_arguments['skip'] = self._limit

        query_filters = self.get_query_from_filters(self._filters)

        return self.coll(alias).find(query_filters, **find_arguments)

    def filter(self, *arguments, **kwargs):
        '''
        Filters a queryset in order to produce a different set of document from subsequent queries.

        Usage::

            User.objects.filter(first_name="Bernardo").filter(last_name="Bernardo").find_all(callback=handle_all)
            # or
            User.objects.filter(first_name="Bernardo", starting_year__gt=2010).find_all(callback=handle_all)

        The available filter options are the same as used in MongoEngine.
        '''
        from motorengine.query_builder.node import Q, QCombination, QNot
        from motorengine.query_builder.transform import validate_fields

        if arguments and len(arguments) == 1 and isinstance(arguments[0], (Q, QNot, QCombination)):
            if self._filters:
                self._filters = self._filters & arguments[0]
            else:
                self._filters = arguments[0]
        else:
            validate_fields(self.__klass__, kwargs)
            if self._filters:
                self._filters = self._filters & Q(**kwargs)
            else:
                if arguments and len(arguments) == 1 and isinstance(arguments[0], dict):
                    self._filters = Q(arguments[0])
                else:
                    self._filters = Q(**kwargs)

        return self

    def filter_not(self, *arguments, **kwargs):
        '''
        Filters a queryset to negate all the filters passed in subsequent queries.

        Usage::

            User.objects.filter_not(first_name="Bernardo").filter_not(last_name="Bernardo").find_all(callback=handle_all)
            # or
            User.objects.filter_not(first_name="Bernardo", starting_year__gt=2010).find_all(callback=handle_all)

        The available filter options are the same as used in MongoEngine.
        '''
        from motorengine.query_builder.node import Q, QCombination, QNot

        if arguments and len(arguments) == 1 and isinstance(arguments[0], (Q, QCombination)):
            self._filters = QNot(arguments[0])
        else:
            self._filters = QNot(Q(**kwargs))

        return self

    def skip(self, skip):
        '''
        Skips N documents before returning in subsequent queries.

        Usage::

            User.objects.skip(20).limit(10).find_all(callback=handle_all)  # even if there are 100s of users,
                                                                           # only users 20-30 will be returned
        '''

        self._skip = skip
        return self


    def limit(self, limit):
        '''
        Limits the number of documents to return in subsequent queries.

        Usage::

            User.objects.limit(10).find_all(callback=handle_all)  # even if there are 100s of users,
                                                                  # only first 10 will be returned
        '''

        self._limit = limit
        return self

    def order_by(self, field_name, direction=ASCENDING):
        '''
        Specified the order to be used when returning documents in subsequent queries.

        Usage::

            from motorengine import DESCENDING  # or ASCENDING

            User.objects.order_by('first_name', direction=DESCENDING).find_all(callback=handle_all)
        '''

        from motorengine.fields.base_field import BaseField
        from motorengine.fields.list_field import ListField

        if isinstance(field_name, (ListField, )):
            raise ValueError("Can't order by a list field. If you meant to order by the size of the list, please use either an Aggregation Pipeline query (look for Document.objects.aggregate) or create an IntField with the size of the list field in your Document.")

        if isinstance(field_name, (BaseField, )):
            field_name = field_name.name

        if field_name not in self.__klass__._fields:
            raise ValueError("Invalid order by field '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))

        field = self.__klass__._fields[field_name]
        self._order_fields.append((field.db_field, direction))
        return self

    def handle_find_all_auto_load_references(self, callback, results):
        def handle(*arguments, **kwargs):
            self.current_count += 1
            if self.current_count == self.result_size:
                self.current_count = None
                self.result_size = None
                callback(results)

        return handle

    def handle_find_all(self, callback, lazy=None):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            result = []
            self.current_count = 0
            self.result_size = len(arguments[0])

            for doc in arguments[0]:
                obj = self.__klass__.from_son(doc)

                result.append(obj)

            if not result:
                callback(result)
                return

            for doc in result:
                if (lazy is not None and not lazy) or not doc.is_lazy:
                    doc.load_references(doc._fields, callback=self.handle_find_all_auto_load_references(callback, result))
                else:
                    self.handle_find_all_auto_load_references(callback, result)()

        return handle

    @return_future
    def find_all(self, callback, lazy=None, alias=None):
        '''
        Returns a list of items in the current queryset collection that match specified filters (if any).

        In order to query a different database, please specify the `alias` of the database to query.

        Usage::

            User.objects.find_all(callback=handle_all_users)

            def handle_all_users(result):
                # do something with result
                # result is None if no users found
                pass
        '''
        to_list_arguments = dict(callback=self.handle_find_all(callback, lazy=lazy))

        if self._limit is not None:
            to_list_arguments['length'] = self._limit
        else:
            to_list_arguments['length'] = DEFAULT_LIMIT

        cursor = self._get_find_cursor(alias=alias)

        self._filters = {}

        cursor.to_list(**to_list_arguments)

    def handle_count(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]
            callback(arguments[0])

        return handle

    @return_future
    def count(self, callback, alias=None):
        '''
        Returns the number of documents in the collection that match the specified filters, if any.
        '''
        cursor = self._get_find_cursor(alias=alias)
        self._filters = {}
        cursor.count(callback=self.handle_count(callback))

    @property
    def aggregate(self):
        return Aggregation(self)

    def handle_ensure_index(self, callback, created_indexes, total_indexes):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            created_indexes.append(arguments[0])

            if len(created_indexes) < total_indexes:
                return

            callback(total_indexes)

        return handle

    @return_future
    def ensure_index(self, callback):
        indexes = []
        for field_name, field in self.__klass__._fields.items():
            if field.unique:
                indexes.append(field.db_field)

        created_indexes = []

        for index in indexes:
            self.coll().ensure_index(
                index,
                unique=True,
                callback=self.handle_ensure_index(
                    callback,
                    created_indexes,
                    len(indexes)
                )
            )

        if not indexes:
            callback(0)
