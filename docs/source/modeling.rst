Modeling
========

.. py:module:: motorengine.document
.. py:module:: motorengine.fields.base_field
.. py:module:: motorengine.fields.string_field
.. py:module:: motorengine.fields.datetime_field
.. py:module:: motorengine.fields.uuid_field
.. py:module:: motorengine.fields.list_field
.. py:module:: motorengine.fields.embedded_document_field
.. py:module:: motorengine.fields.reference_field
.. py:module:: motorengine.fields.url_field
.. py:module:: motorengine.fields.email_field
.. py:module:: motorengine.fields.int_field
.. py:module:: motorengine.fields.boolean_field
.. py:module:: motorengine.fields.float_field
.. py:module:: motorengine.fields.decimal_field
.. py:module:: motorengine.fields.binary_field
.. py:module:: motorengine.fields.json_field

MotorEngine uses the concept of models to interact with MongoDB. To create a model we inherit from the `Document` class:

.. autoclass:: motorengine.document.Document
  :noindex:

Let's say we need an article model with title, description and published_date:

.. testsetup:: modeling_1

    import tornado.ioloop
    from motorengine import connect

    io_loop = tornado.ioloop.IOLoop.instance()

    # you only need to keep track of the DB instance if you connect to multiple databases.
    connect("connecting-test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: modeling_1

    from motorengine.document import Document
    from motorengine.fields import StringField, DateTimeField

    class Article(Document):
        title = StringField(required=True)
        description = StringField(required=True)
        published_date = DateTimeField(auto_now_on_insert=True)

That allows us to create, update, query and remove articles with extreme ease:

.. testsetup:: modeling_2

    from uuid import uuid4
    import tornado.ioloop
    from motorengine import connect
    from motorengine.document import Document
    from motorengine.fields import StringField, DateTimeField

    io_loop = tornado.ioloop.IOLoop.instance()

    # you only need to keep track of the DB instance if you connect to multiple databases.
    connect("connecting-test", host="localhost", port=27017, io_loop=io_loop)

    class Article(Document):
        __collection__ = "ModelingArticles2"
        title = StringField(required=True)
        description = StringField(required=True)
        published_date = DateTimeField(auto_now_on_insert=True)

.. testcode:: modeling_2

    new_title = "Better Title %s" % uuid4()

    def create_article():
        Article.objects.create(
            title="Some Article",
            description="This is an article that really matters.",
            callback=handle_article_created
        )

    def handle_article_created(article):
        article.title = new_title
        article.save(callback=handle_article_updated)

    def handle_article_updated(article):
        Article.objects.filter(title=new_title).find_all(callback=handle_articles_loaded)

    def handle_articles_loaded(articles):
        assert len(articles) == 1
        assert articles[0].title == new_title

        articles[0].delete(callback=handle_article_deleted)

    def handle_article_deleted(number_of_deleted_items):
        try:
            assert number_of_deleted_items == 1
        finally:
            io_loop.stop()

    io_loop.add_timeout(1, create_article)
    io_loop.start()


.. testsetup:: modeling_fields

    from motorengine import *

Base Field
----------

.. autoclass:: motorengine.fields.base_field.BaseField

Available Fields
----------------

.. autoclass:: motorengine.fields.string_field.StringField

.. autoclass:: motorengine.fields.datetime_field.DateTimeField

.. autoclass:: motorengine.fields.uuid_field.UUIDField

.. autoclass:: motorengine.fields.url_field.URLField

.. autoclass:: motorengine.fields.email_field.EmailField

.. autoclass:: motorengine.fields.int_field.IntField

.. autoclass:: motorengine.fields.boolean_field.BooleanField

.. autoclass:: motorengine.fields.float_field.FloatField

.. autoclass:: motorengine.fields.decimal_field.DecimalField

.. autoclass:: motorengine.fields.binary_field.BinaryField

.. autoclass:: motorengine.fields.json_field.JsonField

Multiple Value Fields
---------------------

.. autoclass:: motorengine.fields.list_field.ListField

Embedding vs Referencing
------------------------

Embedding is very useful to improve the retrieval of data from MongoDB. When you have sub-documents that will always be used when retrieving a document (i.e.: comments in a post), it's useful to have them be embedded in the parent document.

On the other hand, if you need a connection to the current document that won't be used in the main use cases for that document, it's a good practice to use a Reference Field. MotorEngine will only load the referenced field if you explicitly ask it to, or if you set `__lazy__` to `False`.

.. autoclass:: motorengine.fields.embedded_document_field.EmbeddedDocumentField

.. autoclass:: motorengine.fields.reference_field.ReferenceField
