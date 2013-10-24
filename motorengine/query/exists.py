#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class ExistsQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field.

    An important reminder is that exists **DOES** match documents that have the specified field **even** if that field value is **NULL**.

    For more information on `$exists` go to http://docs.mongodb.org/manual/reference/operator/query/exists/.

    Usage:

    .. testsetup:: exists_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: exists_query_operator

        class User(Document):
            name = StringField()

        query = Q(name__exists=True)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: exists_query_operator

        {'name': {'$exists': True}}

    '''
    def to_query(self, field_name, value):
        return {
            field_name: {
                "$exists": value
            }
        }

    def get_value(self, field, value):
        return value
