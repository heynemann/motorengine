#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class LesserThanOrEqualQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value lower than or equal to the specified value.

    For more information on `$lte` go to http://docs.mongodb.org/manual/reference/operator/query/lte/.

    Usage:

    .. testsetup:: lte_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: lte_query_operator

        class User(Document):
            age = IntField()

        query = Q(age__lte=21)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: lte_query_operator

        {'age': {'$lte': 21}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$lte": value}
        }
