#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IStartsWithOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field starts with passed string value.

    It is not case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: istartswith_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: istartswith_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__istartswith='bEr')

        query_result = query.to_query(User)

        # Due to dict ordering
        print('{"first_name": {"$options": "%s", "$regex": "%s"}}' % (
            query_result['first_name']['$options'],
            query_result['first_name']['$regex'],
        ))

    The resulting query is:

    .. testoutput:: istartswith_query_operator

        {"first_name": {"$options": "i", "$regex": "^bEr"}}
    '''

    def to_query(self, field_name, value):
        return {
            field_name: {
                "$regex": r'^%s' % value,
                "$options": 'i'
            }
        }
