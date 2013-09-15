MotorEngine MongoDB Async ORM
=============================

.. py:module:: motorengine

:mod:`MotorEngine <motorengine>` is a port of the amazing :mod:`MongoEngine <mongoengine>`.

.. image:: https://travis-ci.org/heynemann/motorengine.png
  :target: https://travis-ci.org/heynemann/motorengine

.. image:: https://pypip.in/v/motorengine/badge.png
  :target: https://crate.io/packages/motorengine/

.. image:: https://pypip.in/d/motorengine/badge.png
  :target: https://crate.io/packages/motorengine/

.. image:: https://coveralls.io/repos/heynemann/motorengine/badge.png?branch=master
  :target: https://coveralls.io/r/heynemann/motorengine?branch=master

Compatibility
-------------

MotorEngine is compatible and tested against python 2.7, 3.3 and pypy.

The tests of compatibility are always run against the current stable version of MongoEngine.

Why use MotorEngine?
--------------------

If you are using tornado, most certainly you don't want your ioLoop to be blocked while doing I/O to mongoDB.

What that means is that :mod:`MotorEngine <motorengine>` allows your tornado instance to keep responding to requests while mongoDB performs your queries.

That's all fine and good, but why choose :mod:`MotorEngine <motorengine>` over using :mod:`Motor <motor>`?

Mainly because :mod:`MotorEngine <motorengine>` helps you in defining consistent documents and makes querying for them really easy.

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

:mod:`MotorEngine <motorengine>` comes baked in with the same fields as :mod:`MongoEngine <mongoengine>`.

What about compatibility?
-------------------------

:mod:`MotorEngine <motorengine>` strives to be 100% compatible with :mod:`MongoEngine <mongoengine>` as far as the data in mongoDB goes.

What that means is that it does not feature the same syntax as :mod:`MongoEngine <mongoengine>`, yet a module saved in :mod:`MongoEngine <mongoengine>` can be read with :mod:`MotorEngine <motorengine>` and vice-versa.

It does not make sense to support the exact same syntax, considering the asynchronous nature of :mod:`MotorEngine <motorengine>`.

Let's see how you query documents using :mod:`MotorEngine <motorengine>`:

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

