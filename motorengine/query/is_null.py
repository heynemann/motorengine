#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IsNullQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents that have the specified field with a null value (or not null if set to False).

    This operator uses $exists and $ne for the **not null** scenario.

    For more information on `$exists` go to http://docs.mongodb.org/manual/reference/operator/query/exists/.

    For more information on `$ne` go to http://docs.mongodb.org/manual/reference/operator/query/ne/.

    Usage:

    .. testsetup:: isnull_query_operator

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

    .. testcode:: isnull_query_operator

        class User(Document):
            email = StringField()

        query = Q(email__is_null=False)

        query_result = query.to_query(User)

        print(query_result)

    The resulting query is:

    .. testoutput:: isnull_query_operator

        {'email': {'$ne': None, '$exists': True}}

    '''

    def to_query(self, field_name, value):
        if value:
            return {
                field_name: None
            }
        else:
            return {
                field_name: {
                    "$exists": True,
                    "$ne": None
                }
            }

    def get_value(self, field, value):
        return value
