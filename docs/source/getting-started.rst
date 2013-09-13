Getting Started
===============

Installing
----------

MotorEngine can be easily installed with pip, using::

    $ pip install motorengine

If you wish to install it from the source code, you can install it using::

    $ pip install https://github.com/heynemann/motorengine/archive/master.zip

Connecting to a Database
------------------------

.. py:module:: motorengine
.. py:module:: motorengine.connection
.. autofunction:: motorengine.connection.connect

.. code-block:: python

    from motorengine import connect

    def main():
        # instantiate tornado server and apps so we get io_loop instance

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=4445, io_loop=io_loop)  # you only need to keep track of the
                                                                       # DB instance if you connect to multiple databases.

Modeling a Document
-------------------

.. py:module:: motorengine.document
.. autoclass:: motorengine.document.Document

.. code-block:: python

    from motorengine import Document

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        employee_id = IntField(required=True)

Creating a new Instance
-----------------------

.. py:module:: motorengine.document
.. automethod:: motorengine.document.BaseDocument.save

Due to the asynchronous nature of MotorEngine, you are required to handle saving in a callback (or using yield method with tornado.concurrent).

.. code-block:: python

    def create_employee():
        emp = yield Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532).save()
        assert emp.employee_id == 1532
