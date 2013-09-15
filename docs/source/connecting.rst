Connecting
==========

.. py:module:: motorengine
  :noindex:
.. py:module:: motorengine.connection
  :noindex:

Simple Connection
-----------------

MotorEngine supports connecting to the database using a myriad of options via the `connect` method.

.. autofunction:: motorengine.connection.connect(db, host="localhost", port=4445, io_loop=io_loop)
  :noindex:

.. code-block:: python

    from motorengine import connect

    def main():
        # instantiate tornado server and apps so we get io_loop instance

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=4445, io_loop=io_loop)  # you only need to keep track of the
                                                                       # DB instance if you connect to multiple databases.

Replica Sets
------------

.. autofunction:: motorengine.connection.connect(db, host="localhost:27017,localhost:27018", replicaSet="myRs", io_loop=self.io_loop)
  :noindex:

The major difference here is that instead of passing a single `host`, you need to pass all the `host:port` entries, comma-separated in the `host` parameter.

You also need to specify the name of the Replica Set in the `replicaSet` parameter (the naming is not pythonic to conform to Motor and thus to pyMongo).

Multiple Databases
------------------

.. autofunction:: motorengine.connection.connect(db, alias="db1", host="localhost", port=4445, io_loop=io_loop)
  :noindex:

Connecting to multiple databases is as simple as specifying a different alias to each connection.

Let's say you need to connect to an users and a posts databases:

.. code-block:: python

    from motorengine import connect

    connect("posts", host="mongodb.acme.com", port=4445, io_loop=io_loop)  # the posts database is the default
    connect("users", alias="users",  host="mongodb.acme.com", port=4445, io_loop=io_loop)  # the users database uses an alias

Now when querying for users we'll just specify the alias we want to use:

.. code-block:: python

    User.objects.find_all(alias="users")  # will query the users database
