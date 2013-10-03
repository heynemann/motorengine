#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections

from tornado.concurrent import return_future

from motorengine import ASCENDING
from motorengine.connection import get_connection
from motorengine.fields.embedded_document_field import EmbeddedDocumentField
from motorengine.query.lesser_than import LesserThanQueryOperator
from motorengine.query.greater_than import GreaterThanQueryOperator
from motorengine.query.lesser_than_or_equal import LesserThanOrEqualQueryOperator
from motorengine.query.greater_than_or_equal import GreaterThanOrEqualQueryOperator
from motorengine.query.exists import ExistsQueryOperator
from motorengine.query.is_null import IsNullQueryOperator


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = 300
        self._order_fields = []

        self.available_query_operators = {
            'lt': LesserThanQueryOperator,
            'gt': GreaterThanQueryOperator,
            'lte': LesserThanOrEqualQueryOperator,
            'gte': GreaterThanOrEqualQueryOperator,
            'exists': ExistsQueryOperator,
            'is_null': IsNullQueryOperator
        }

    @property
    def is_lazy(self):
        return self.__klass__.__lazy__

    def coll(self, alias):
        if alias is not None:
            conn = get_connection(alias=alias)
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
            connect("test", host="localhost", port=4445, io_loop=io_loop)

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

    def save(self, document, callback, alias=None):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))

        if document.validate():
            doc = document.to_son()
            if document._id is not None:
                self.coll(alias).update({'_id': document._id}, doc, callback=self.handle_update(document, callback))
            else:
                self.coll(alias).insert(doc, callback=self.handle_save(document, callback))

    @return_future
    def delete(self, callback=None, alias=None):
        '''
        Removes all instance of this document that match the specified filters (if any).

        .. testsetup:: saving_delete

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstances"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=4445, io_loop=io_loop)

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
        if id is None and not kwargs:
            raise RuntimeError("Either an id or a filter must be provided to get")

        if id is not None:
            filters = {
                "_id": id
            }
        else:
            filters = self.to_filters(**kwargs)
            filters = self.get_query_from_filters(filters)

        self.coll(alias).find_one(filters, callback=self.handle_get(callback))

    def to_filters(self, **kwargs):
        from motorengine import Document  # to avoid circular dependency

        filters = {}
        for field_name, value in kwargs.items():
            original_field_name = field_name
            field_db_name = None
            field_value = None

            operator = ""
            if '__' in field_name:
                filter_values = field_name.split('__')
                operator = filter_values[-1]
                field_name = ".".join(filter_values[:-1])

            if operator and operator not in self.available_query_operators:
                field_name = "%s.%s" % (field_name, operator)
                operator = ""

            if '.' in field_name:
                values = field_name.split('.')
                obj = self.__klass__
                fields = []

                for field_index, partial_field_name in enumerate(values):
                    if not partial_field_name in obj._fields:
                        raise ValueError("Invalid filter '%s': Field '%s' not found in '%s'." % (
                            original_field_name,
                            partial_field_name,
                            obj.__name__
                        ))

                    if issubclass(obj, Document):
                        field = obj._fields[partial_field_name]
                    else:
                        field = obj

                    fields.append(field.db_field)

                    obj = getattr(obj, partial_field_name)

                    is_last = field_index == len(values) - 1
                    if is_last:
                        field_value = value
                        field_db_name = ".".join(fields)
                        continue

                    if not isinstance(obj, EmbeddedDocumentField):
                        raise ValueError(
                            ("Invalid filter '%s': Invalid operator (if this is a sub-property, then it must be "
                                "used in embedded document fields).") % (
                                original_field_name,
                            )
                        )

                    obj = obj.embedded_type
            else:
                if field_name not in self.__klass__._fields:
                    raise ValueError("Invalid filter '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))

                if operator and operator not in self.available_query_operators:
                    raise ValueError("Invalid filter '%s': Operator not found '%s'." % (original_field_name, operator))

                field = self.__klass__._fields[field_name]
                field_db_name = field.db_field
                field_value = value

            if not field_db_name in filters:
                filters[field_db_name] = []

            filters[field_db_name].append({
                "operator": operator,
                "value": field_value,
                "field": field
            })

        return filters

    def get_query_from_filters(self, filters):
        result = {}

        for filter_name, filter_items in filters.items():
            for filter_desc in filter_items:
                operator, filter_value, field = filter_desc['operator'], filter_desc['value'], filter_desc['field']

                if not operator:
                    result[filter_name] = field.to_son(filter_value)
                else:
                    operator = self.available_query_operators[operator]()
                    value = operator.get_value(field, filter_value)
                    query = operator.to_query(filter_name, value)

                    self.update(result, query)

        return result

    # from http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    def update(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = self.update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def _get_find_cursor(self, alias):
        find_arguments = {}

        if self._order_fields:
            find_arguments['sort'] = self._order_fields

        query_filters = self.get_query_from_filters(self._filters)

        return self.coll(alias).find(query_filters, **find_arguments)

    def filter(self, **kwargs):
        '''
        Filters a queryset in order to produce a different set of document from subsequent queries.

        Usage::

            User.objects.filter(first_name="Bernardo").filter(last_name="Bernardo").find_all(callback="handle_all")
            # or
            User.objects.filter(first_name="Bernardo", starting_year__gt=2010).find_all(callback=handle_all)

        The available filter options are the same as used in MongoEngine.
        '''
        filters = self.to_filters(**kwargs)
        self._filters.update(filters)
        return self

    def limit(self, limit):
        '''
        Limits the number of documents to return in subsequent queries.

        Usage::

            User.objects.limit(10).find_all(callback="handle_all")  # even if there are 100s of users,
                                                                    # only first 10 will be returned
        '''

        self._limit = limit
        return self

    def order_by(self, field_name, direction=ASCENDING):
        '''
        Specified the order to be used when returning documents in subsequent queries.

        Usage::

            from motorengine import DESCENDING  # or ASCENDING

            User.objects.order_by('first_name', direction=DESCENDING).find_all(callback="handle_all")
        '''

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
                    doc.load_references(callback=self.handle_find_all_auto_load_references(callback, result))
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

        self._get_find_cursor(alias=alias).to_list(**to_list_arguments)

    def handle_count(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]
            callback(arguments[0])

        return handle

    @return_future
    def count(self, callback, alias=None):
        '''
        Returns the number of documents in the collection that match the specified filters (if any).
        '''
        self._get_find_cursor(alias=alias).count(callback=self.handle_count(callback))
