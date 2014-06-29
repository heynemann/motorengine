Querying
========

MotorEngine supports a vast array of query operators in MongoDB. There are two ways of querying documents: using the **queryset methods** (filter, filter_not and the likes) or a **Q** object.

Querying with filter methods
----------------------------

.. automethod:: motorengine.queryset.QuerySet.filter

.. automethod:: motorengine.queryset.QuerySet.filter_not

Querying with Q
---------------

.. autoclass:: motorengine.query_builder.node.Q

The **Q** object can be combined using python's binary operators **|** and **&**. Do not confuse those with the **and** and **or** keywords. Those keywords won't call the **__and__** and **__or__** methods in the Q class that are required for the combination of queries.

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

        # the resulting query should be similar to:
        # {'$or': [{'last_update': None}, {'is_active': True, 'last_update': {'$lt': datetime.datetime(2010, 1, 1, 0, 0)}}]}

        assert '$or' in query_result

        or_query = query_result['$or']
        assert len(or_query) == 2
        assert 'last_update' in or_query[0]
        assert 'is_active' in or_query[1]
        assert 'last_update' in or_query[1]

Query Operators
---------------

Query operators can be used when specified after a given field, like::

    Q(field_name__operator_name=operator_value)

MotorEngine supports the following query operators:

.. autoclass:: motorengine.query.exists.ExistsQueryOperator

.. autoclass:: motorengine.query.greater_than.GreaterThanQueryOperator

.. autoclass:: motorengine.query.greater_than_or_equal.GreaterThanOrEqualQueryOperator

.. autoclass:: motorengine.query.lesser_than.LesserThanQueryOperator

.. autoclass:: motorengine.query.lesser_than_or_equal.LesserThanOrEqualQueryOperator

.. autoclass:: motorengine.query.in_operator.InQueryOperator

.. autoclass:: motorengine.query.is_null.IsNullQueryOperator

.. autoclass:: motorengine.query.not_equal.NotEqualQueryOperator

Querying with Raw Queries
-------------------------

Even though motorengine strives to provide an interface for queries that makes naming fields and documents transparent, using mongodb raw queries is still supported, both in the filter method and the Q class.

In order to use raw queries, just pass the same object you would use in mongodb:

    .. testsetup:: querying_with_raw_queries

        from time import time
        import tornado.ioloop

        from motorengine import *

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=27017, io_loop=io_loop)

    .. testcode:: querying_with_raw_queries

        import tornado.ioloop

        class Address(Document):
            __collection__ = "QueryingWithRawQueryAddress"
            street = StringField()

        class User(Document):
            __collection__ = "QueryingWithRawQueryUser"
            addresses = ListField(EmbeddedDocumentField(Address))
            name = StringField()

        def create_user():
            user = User(name="Bernardo", addresses=[Address(street="Infinite Loop")])
            user.save(callback=handle_user_created)

        def handle_user_created(user):
            User.objects.filter({
                "addresses": {
                    "street": "Infinite Loop"
                }
            }).find_all(callback=handle_find_user)

        def handle_find_user(users):
            try:
                assert users[0].name == "Bernardo", users
                assert users[0].addresses[0].street == "Infinite Loop", users
            finally:
                io_loop.stop()

        io_loop.add_timeout(1, create_user)
        io_loop.start()
