#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class LesserThanQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value lower than the specified value.

    For more information on `$lt` go to http://docs.mongodb.org/manual/reference/operator/query/lt/.

    Usage:

    .. testsetup:: lt_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: lt_query_operator

        class User(Document):
            age = IntField()

        query = Q(age__lt=20)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: lt_query_operator

        {'age': {'$lt': 20}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$lt": value}
        }
