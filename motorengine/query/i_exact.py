#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IExactOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field is exactly as passed string value.

    It is not case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: iexact_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: iexact_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__iexact='bErNaRdO')

        query_result = query.to_query(User)

        # Due to dict ordering
        print('{"first_name": {"$options": "%s", "$regex": "%s"}}' % (
            query_result['first_name']['$options'],
            query_result['first_name']['$regex'],
        ))

    The resulting query is:

    .. testoutput:: iexact_query_operator

        {"first_name": {"$options": "i", "$regex": "^bErNaRdO$"}}
    '''

    def to_query(self, field_name, value):
        return {
            field_name: {
                "$regex": r'^%s$' % value,
                "$options": 'i'
            }
        }
