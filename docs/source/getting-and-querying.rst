Querying
========

MotorEngine supports a vast array of query operators in MongoDB. There are two ways of querying documents: using the **queryset methods** (filter, filter_not and the likes) or a **Q** object.

.. automethod:: motorengine.queryset.QuerySet.filter

.. automethod:: motorengine.queryset.QuerySet.filter_not

.. autoclass:: motorengine.query_builder.node.Q

Querying with Q
---------------

The **Q** object can be combined using python's binary operators **|** and **&**. Do not confuse those with the **and** and **or** key words. Those keywords won't call the **__and__** and **__or__** methods in the Q class that are required for the combination of queries.

Let's look at an example of querying for a more specific document. Say we want to find the user that either has a **null** date of last update or is active with a date of last_update lesser than 2010:

    .. testsetup:: querying_with_Q_and_or

        from datetime import datetime

        import tornado.ioloop

        from motorengine import *

        class User(Document):
            __collection__ = "UserQueryingWithQAndOr"
            last_update = DateTimeField()
            is_active = BooleanField()

    .. testcode:: querying_with_Q_and_or

        query = Q(last_update__is_null=True) | (Q(is_active=True) & Q(last_update__lt=datetime(2010, 1, 1, 0, 0, 0)))

        query_result = query.to_query(User)

        assert len(query_result['$or']) == 2

        # query_result is now:
        # {
        #     '$or': [
        #         {'last_update': None},
        #         {'is_active': 1, 'last_update': {'$lt': datetime.datetime(2010, 1, 1, 0, 0)}}
        #     ]
        # }
