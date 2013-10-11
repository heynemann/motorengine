MotorEngine MongoDB Async ORM
=============================

.. py:module:: motorengine

`MotorEngine`_ is a port of the amazing `MongoEngine`_.

.. image:: https://travis-ci.org/heynemann/motorengine.png
  :target: https://travis-ci.org/heynemann/motorengine

.. image:: https://pypip.in/v/motorengine/badge.png
  :target: https://crate.io/packages/motorengine/

.. image:: https://pypip.in/d/motorengine/badge.png
  :target: https://crate.io/packages/motorengine/

.. image:: https://coveralls.io/repos/heynemann/motorengine/badge.png?branch=master
  :target: https://coveralls.io/r/heynemann/motorengine?branch=master

Supported Versions
------------------

`MotorEngine`_ is compatible and tested against python 2.7, 3.3 and pypy.

`MotorEngine`_ requires MongoDB 2.2+ due to usage of the `Aggregation Pipeline`_.

The tests of compatibility are always run against the current stable version of `MongoEngine`_.

Why use MotorEngine?
--------------------

If you are using tornado, most certainly you don't want your ioLoop to be blocked while doing I/O to mongoDB.

What that means is that `MotorEngine`_ allows your tornado instance to keep responding to requests while mongoDB performs your queries.

That's all fine and good, but why choose `MotorEngine`_?

Mainly because `MotorEngine`_ helps you in defining consistent documents and makes querying for them really easy.

Defining Documents
------------------

Defining a new document is as easy as:

.. code-block:: python

    from motorengine import Document, StringField

    class User(Document):
        __collection__ = "users"  # optional. if no collection is specified, class name is used.

        first_name = StringField(required=True)
        last_name = StringField(required=True)

        @property
        def full_name(self):
            return "%s, %s" % (self.last_name, self.first_name)

`MotorEngine`_ comes baked in with the same fields as `MongoEngine`_.

What about compatibility?
-------------------------

`MotorEngine`_ strives to be 100% compatible with `MongoEngine`_ as far as the data in mongoDB goes.

What that means is that it does not feature the same syntax as `MongoEngine`_ and vice-versa.

It does not make sense to support the exact same syntax, considering the asynchronous nature of `MotorEngine`_.

Let's see how you query documents using `MotorEngine`_:

.. code-block:: python

    def get_active_users(callback):
        User.objects.filter(active=True).find_all(callback)

    def handle_get_active_users(users):
        # do something with the users
        pass

    get_active_users(handle_get_active_users)

Or if you are using the new style of doing asynchronous operations in Tornado:

.. code-block:: python

    def get_active_users():
        users = yield User.objects.filter(active=True).find_all()
        return users

Contents
--------

.. toctree::
  :maxdepth: 2

  getting-started
  connecting
  modeling
  saving
  getting-and-querying


.. _MotorEngine: http://motorengine.readthedocs.org/en/latest/
.. _MongoEngine: http://docs.mongoengine.org/en/latest/
.. _Motor: http://motor.readthedocs.org/en/stable/
.. _Aggregation Pipeline: http://docs.mongodb.org/manual/reference/method/db.collection.aggregate/#db.collection.aggregate
