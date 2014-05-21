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

.. autofunction:: motorengine.connection.connect

.. testsetup:: connecting

    import tornado.ioloop
    from motorengine import connect

.. testcode:: connecting

    # instantiate tornado server and apps so we get io_loop instance

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)  # you only need to keep track of the
                                                                   # DB instance if you connect to multiple databases.

Modeling a Document
-------------------

.. autoclass:: motorengine.document.Document

.. testsetup:: modeling

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

.. testcode:: modeling

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        employee_id = IntField(required=True)

Creating a new instance
-----------------------

.. automethod:: motorengine.document.BaseDocument.save

Due to the asynchronous nature of MotorEngine, you are required to handle saving in a callback (or using yield method with tornado.concurrent).

.. testsetup:: creating_new_instance

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: creating_new_instance

    def create_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532)
        emp.save(handle_employee_saved)

    def handle_employee_saved(emp):
        try:
            assert emp is not None
            assert emp.employee_id == 1532
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, create_employee)
    io_loop.start()

Updating an instance
--------------------

.. automethod:: motorengine.document.BaseDocument.save

Updating an instance is as easy as changing a property and calling save again:

.. testsetup:: updating_instance

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: updating_instance

    def update_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532)
        emp.save(handle_employee_created)

    def handle_employee_created(emp):
        emp.employee_id = 1534
        emp.save(handle_employee_updated)

    def handle_employee_updated(emp):
        try:
            assert emp.employee_id == 1534
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, update_employee)
    io_loop.start()


Getting an instance
-------------------

.. automethod:: motorengine.queryset.QuerySet.get

To get an object by id, you must specify the ObjectId that the instance got created with. This method takes a string as well and transforms it into a :mod:`bson.objectid.ObjectId <bson.objectid.ObjectId>`.

.. testsetup:: getting_instance

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: getting_instance

    def create_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1538)
        emp.save(handle_employee_saved)

    def handle_employee_saved(emp):
        Employee.objects.get(emp._id, callback=handle_employee_loaded)  # every object in MotorEngine has an 
                                                                        # _id property with its ObjectId.

    def handle_employee_loaded(emp):
        try:
            assert emp is not None
            assert emp.employee_id == 1538
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, create_employee)
    io_loop.start()

Querying collections
--------------------

To query a collection in mongo, we use the `find_all` method.

.. automethod:: motorengine.queryset.QuerySet.find_all

If you want to filter a collection, just chain calls to `filter`:

.. automethod:: motorengine.queryset.QuerySet.filter

To limit a queryset to just return a maximum number of documents, use the `limit` method:

.. automethod:: motorengine.queryset.QuerySet.limit

Ordering the results is achieved with the `order_by` method:

.. automethod:: motorengine.queryset.QuerySet.order_by

All of these options can be combined to really tune how to get items:

.. testsetup:: filtering_instances

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: filtering_instances

    def create_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1538)
        emp.save(handle_employee_saved)

    def handle_employee_saved(emp):
      # return the first 10 employees ordered by last_name that joined after 2010
      Employee.objects \
              .limit(10) \
              .order_by("last_name") \
              .filter(last_name="Heynemann") \
              .find_all(callback=handle_employees_loaded)

    def handle_employees_loaded(employees):
        try:
            assert len(employees) > 0
            assert employees[0].last_name == "Heynemann"
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, create_employee)
    io_loop.start()

Counting documents in collections
---------------------------------

.. automethod:: motorengine.queryset.QuerySet.count

.. testsetup:: counting_instances

    import tornado.ioloop
    from motorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringCountInstancesEmployee"
        employee_id = IntField(required=True)

    io_loop = tornado.ioloop.IOLoop.instance()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: counting_instances

    def get_employees():
      Employee.objects.count(callback=handle_count)

    def handle_count(number_of_employees):
        try:
            assert number_of_employees == 0
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, get_employees)
    io_loop.start()

