#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class EndsWithOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field ends with passed string value.

    It is case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: endswith_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: endswith_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__endswith='do')

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: endswith_query_operator

        {'first_name': {'$regex': 'do$'}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$regex": r'%s$' %value}
        }
