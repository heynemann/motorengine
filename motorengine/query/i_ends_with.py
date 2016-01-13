#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IEndsWithOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field ends with passed string value.

    It is not case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: iendswith_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: iendswith_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__iendswith='Do')

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: iendswith_query_operator

        {'name': {'$regex': 'Do$', '$options': 'i'}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {
                "$regex": r'%s$' %value,
                "$options": 'i'
            }
        }
