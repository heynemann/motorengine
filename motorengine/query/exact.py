#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class ExactOperator(QueryOperator):
    '''
    Query operator used to return all documents which specified field is exactly as passed string value.

    It is case sensitive.

    For more information on `$regex` go to https://docs.mongodb.org/manual/reference/operator/query/regex/

    Usage:

    .. testsetup:: exact_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: exact_query_operator

        class User(Document):
            first_name = StringField()

        query = Q(first_name__exact='Bernardo')

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: exact_query_operator

        {'first_name': {'$regex': '^Bernardo$'}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$regex": r'^%s$' %value}
        }
