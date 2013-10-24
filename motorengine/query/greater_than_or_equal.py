#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class GreaterThanOrEqualQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value greater than or equal to the specified value.

    For more information on `$gte` go to http://docs.mongodb.org/manual/reference/operator/query/gte/.

    Usage:

    .. testsetup:: gte_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: gte_query_operator

        class User(Document):
            age = IntField()

        query = Q(age__gte=21)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: gte_query_operator

        {'age': {'$gte': 21}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$gte": value}
        }
