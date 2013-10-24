#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class NotEqualQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a value that's not equal to the specified value.

    For more information on `$ne` go to http://docs.mongodb.org/manual/reference/operator/query/ne/.

    Usage:

    .. testsetup:: ne_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: ne_query_operator

        class User(Document):
            email = StringField()

        query = Q(email__ne="heynemann@gmail.com")

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: ne_query_operator

        {'email': {'$ne': 'heynemann@gmail.com'}}

    '''

    def to_query(self, field_name, value):
        return {
            field_name: {"$ne": value}
        }
