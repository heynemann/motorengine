Saving instances
================

Creating new instances of a document
------------------------------------

The easiest way of creating a new instance of a document is using `Document.objects.create`. Alternatively, you can create a new instance and then call `save` on it.

.. automethod:: motorengine.queryset.QuerySet.create

.. automethod:: motorengine.document.Document.save

    .. testsetup:: saving_save

        import tornado.ioloop
        from motorengine import *

        class User(Document):
            __collection__ = "UserSavingInstances"
            name = StringField()

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=4445, io_loop=io_loop)

    .. testcode:: saving_save

        def handle_user_created(user):
            try:
                assert user.name == "Bernardo"
            finally:
                io_loop.stop()

        def create_user():
            user = User(name="Bernardo")
            user.save(callback=handle_user_created)

        io_loop.add_timeout(1, create_user)
        io_loop.start()

Updating instances
------------------

To update an instance, just make the needed changes to an instance and then call `save`.

.. automethod:: motorengine.document.Document.save

    .. testsetup:: saving_update

        import tornado.ioloop
        from motorengine import *

        class User(Document):
            __collection__ = "UserUpdatingInstances"
            name = StringField()

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=4445, io_loop=io_loop)

    .. testcode:: saving_update

        def handle_user_created(user):
            user.name = "Heynemann"
            user.save(callback=handle_user_updated)

        def handle_user_updated(user):
            try:
                assert user.name == "Heynemann"
            finally:
                io_loop.stop()

        def create_user():
            user = User(name="Bernardo")
            user.save(callback=handle_user_created)

        io_loop.add_timeout(1, create_user)
        io_loop.start()

Deleting instances
------------------

Deleting an instance can be easily accomplished by just calling `delete` on it:

.. automethod:: motorengine.document.Document.delete

Sometimes, though, the requirements are to remove a few documents (or all of them) at a time. MotorEngine also supports deleting using filters in the document queryset.

.. automethod:: motorengine.queryset.QuerySet.delete



