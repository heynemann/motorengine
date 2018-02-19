#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class StartsWithOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field starts with passed string value.

    It is case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: startswith_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: startswith_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__startswith='Ber')

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: startswith_query_operator

        {'first_name': {'$regex': '^Ber'}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$regex": r'^%s' %value}
        }
