#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class GreaterThanQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value greater than the specified value.

    For more information on `$gt` go to http://docs.mongodb.org/manual/reference/operator/query/gt/.

    Usage:

    .. testsetup:: gt_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: gt_query_operator

        class User(Document):
            age = IntField()

        query = Q(age__gt=20)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: gt_query_operator

        {'age': {'$gt': 20}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$gt": value}
        }
