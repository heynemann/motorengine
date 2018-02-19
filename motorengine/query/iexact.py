#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IExactQueryOperator(QueryOperator):
    '''
    Query operator used to return all documents which match irrespective of insentive case.
    For more information on "$regex" go to http://docs.mongodb.org/manual/reference/operator/query/regex/.
    Usage:
    .. testsetup:: iexact_query_operator
        from datetime import datetime
        import tornado.ioloop
        from motorengine import *
    .. testcode:: iexact_query_operator
        class User(Document):
            name = StringField()
        query = Q(name__iexact="amanda")
        query_result = query.to_query(User)
        print(query_result)
    The resulting query is:
    .. testoutput:: iexact_query_operator
        {'name': {'$regex': '^amanda$', '$options': 'i'}}
    '''
    def to_query(self, field_name, value):
        return {
            field_name: {
                "$regex": '^{}$'.format(value),
                "$options": 'i'
            }
        }
