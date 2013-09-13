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

Creating a new instance
-----------------------

.. py:module:: motorengine.document
.. automethod:: motorengine.document.BaseDocument.save

Due to the asynchronous nature of MotorEngine, you are required to handle saving in a callback (or using yield method with tornado.concurrent).

.. code-block:: python

    def create_employee():
        emp = yield Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532).save()
        assert emp.employee_id == 1532

Updating an instance
--------------------

Updating an instance is as easy as changing a property and calling save again:

.. code-block:: python

    def update_employee():
        emp = yield Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532).save()

        emp.employee_id = 1993
        yield emp.save()

Getting an instance
-------------------

.. automethod:: motorengine.queryset.QuerySet.get

In order to get an object by id, you must specify the ObjectId that the instance got created with. This method takes a string as well and transforms it into a :mod:`bson.objectid.ObjectId <bson.objectid.ObjectId>`.

.. code-block:: python

    def get_employee_by_id(object_id):
        emp = yield Employee.objects.get(object_id)
        return emp

    emp = yield Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532).save()

    loaded_emp = get_employee_by_id(emp._id)  # every object in MotorEngine has an _id property with
                                              # it's ObjectId.

Querying collections
--------------------

To query a collection in mongo, we use the `find_all` method.

.. automethod:: motorengine.queryset.QuerySet.find_all

