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
.. py:module:: motorengine.fields.float_field
.. py:module:: motorengine.fields.decimal_field
.. py:module:: motorengine.fields.binary_field
.. py:module:: motorengine.fields.json_field

MotorEngine uses the concept of models to interact with MongoDB. To create a model we inherif from the `Document` class:

.. autoclass:: motorengine.document.Document
  :noindex:

Let's say we need an article model with title, description and published_date:

.. code-block:: python

    from motorengine import Document, StringField, DateTimeField

    class Article(Document):
        title = StringField(required=True)
        description = StringField(required=True)
        published_date = DateTimeField(auto_now=True)

That allows us to create, update, query and remove articles with extreme ease:

.. code-block:: python

    article = yield Article.objects.create(title="Some Article", description="This is an article that really matters.")

    article.title = "Better Title"
    yield article.save()

    articles = yield Article.objects.filter(title="Better Title").find_all()
    # articles[0] is article

    yield article.delete()

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

.. autoclass:: motorengine.fields.float_field.FloatField

.. autoclass:: motorengine.fields.decimal_field.DecimalField

.. autoclass:: motorengine.fields.binary_field.BinaryField

.. autoclass:: motorengine.fields.json_field.JsonField

Multiple Value Fields
---------------------

.. autoclass:: motorengine.fields.list_field.ListField

Embedding vs Referencing
------------------------

.. autoclass:: motorengine.fields.embedded_document_field.EmbeddedDocumentField

.. autoclass:: motorengine.fields.reference_field.ReferenceField
