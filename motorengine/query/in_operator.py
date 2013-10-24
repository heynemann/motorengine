#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class InQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value that match one of the values in the specified range.

    If the specified field is a ListField, then at least one of the items in the field must match at least one of the items in the specified range.

    For more information on `$in` go to http://docs.mongodb.org/manual/reference/operator/query/in/.

    Usage:

    .. testsetup:: in_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: in_query_operator

        class User(Document):
            age = IntField()

        query = Q(age__in=[20, 21, 22, 23, 24])

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: in_query_operator

        {'age': {'$in': [20, 21, 22, 23, 24]}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {
                "$in": value
            }
        }

    def get_value(self, field, value):
        return [field.to_son(val) for val in value]
