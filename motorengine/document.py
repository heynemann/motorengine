#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
from tornado.concurrent import return_future

from motorengine.metaclasses import DocumentMetaClass
from motorengine.errors import InvalidDocumentError, LoadReferencesRequiredError


AUTHORIZED_FIELDS = [
    '_id', '_values', '_reference_loaded_fields', 'is_partly_loaded'
]


class BaseDocument(object):
    def __init__(
        self, _is_partly_loaded=False, _reference_loaded_fields=None, **kw
    ):
        """
        :param _is_partly_loaded: is a flag that indicates if the document was
        loaded partly (with `only`, `exlude`, `fields`). Default: False.
        :param _reference_loaded_fields: dict that contains projections for
        reference fields if any. Default: None.
        :param kw: pairs of fields of the document and their values
        """
        from motorengine.fields.dynamic_field import DynamicField

        self._id = kw.pop('_id', None)
        self._values = {}
        self.is_partly_loaded = _is_partly_loaded

        if _reference_loaded_fields:
            self._reference_loaded_fields = _reference_loaded_fields
        else:
            self._reference_loaded_fields = {}

        for key, field in self._fields.items():
            if callable(field.default):
                self._values[field.name] = field.default()
            else:
                self._values[field.name] = field.default

        for key, value in kw.items():
            if key not in self._fields:
                self._fields[key] = DynamicField(db_field="_%s" % key.lstrip('_'))
            self._values[key] = value

    @classmethod
    @return_future
    def ensure_index(cls, callback=None):
        cls.objects.ensure_index(callback=callback)

    @property
    def is_lazy(self):
        return self.__class__.__lazy__

    def is_list_field(self, field):
        from motorengine.fields.list_field import ListField
        return isinstance(field, ListField) or (isinstance(field, type) and issubclass(field, ListField))

    def is_reference_field(self, field):
        from motorengine.fields.reference_field import ReferenceField
        return isinstance(field, ReferenceField) or (isinstance(field, type) and issubclass(field, ReferenceField))

    def is_embedded_field(self, field):
        from motorengine.fields.embedded_document_field import EmbeddedDocumentField
        return isinstance(field, EmbeddedDocumentField) or (isinstance(field, type) and issubclass(field, EmbeddedDocumentField))

    @classmethod
    def from_son(cls, dic, _is_partly_loaded=False, _reference_loaded_fields=None):
        field_values = {}
        for name, value in dic.items():
            field = cls.get_field_by_db_name(name)
            if field:
                field_values[field.name] = cls._fields[field.name].from_son(value)
            else:
                field_values[name] = value

        return cls(
            _is_partly_loaded=_is_partly_loaded,
            _reference_loaded_fields=_reference_loaded_fields,
            **field_values
        )

    def to_son(self):
        data = dict()

        for name, field in self._fields.items():
            value = self.get_field_value(name)
            if field.sparse and field.is_empty(value):
                continue
            data[field.db_field] = field.to_son(value)

        return data

    def validate(self):
        return self.validate_fields()

    def validate_fields(self):
        for name, field in self._fields.items():

            value = self.get_field_value(name)

            if field.required and field.is_empty(value):
                raise InvalidDocumentError("Field '%s' is required." % name)
            if not field.validate(value):
                raise InvalidDocumentError("Field '%s' must be valid." % name)

        return True

    @return_future
    def save(self, callback, alias=None):
        '''
        Creates or updates the current instance of this document.
        '''
        self.objects.save(self, callback=callback, alias=alias)

    @return_future
    def delete(self, callback, alias=None):
        '''
        Deletes the current instance of this Document.

        .. testsetup:: saving_delete_one

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstance"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete_one

            def handle_user_created(user):
                user.delete(callback=handle_user_deleted)

            def handle_user_deleted(number_of_deleted_items):
                try:
                    assert number_of_deleted_items == 1
                finally:
                    io_loop.stop()

            def create_user():
                user = User(name="Bernardo")
                user.save(callback=handle_user_created)

            io_loop.add_timeout(1, create_user)
            io_loop.start()
        '''
        self.objects.remove(instance=self, callback=callback, alias=alias)

    def fill_values_collection(self, collection, field_name, value):
        collection[field_name] = value

    def fill_list_values_collection(self, collection, field_name, value):
        if field_name not in collection:
            collection[field_name] = []
        collection[field_name].append(value)

    def handle_load_reference(self, callback, references, reference_count, values_collection, field_name, fill_values_method=None):
        if fill_values_method is None:
            fill_values_method = self.fill_values_collection

        def handle(*args, **kw):
            fill_values_method(values_collection, field_name, args[0])

            if reference_count > 0:
                references.pop()

            if len(references) == 0:
                callback({
                    'loaded_reference_count': reference_count,
                    'loaded_values': values_collection
                })

        return handle

    @return_future
    def load_references(self, fields=None, callback=None, alias=None):
        if callback is None:
            raise ValueError("Callback can't be None")

        references = self.find_references(document=self, fields=fields)
        reference_count = len(references)

        if not reference_count:
            callback({
                'loaded_reference_count': reference_count,
                'loaded_values': []
            })
            return

        for dereference_function, document_id, values_collection, field_name, fill_values_method in references:
            dereference_function(
                document_id,
                callback=self.handle_load_reference(
                    callback=callback,
                    references=references,
                    reference_count=reference_count,
                    values_collection=values_collection,
                    field_name=field_name,
                    fill_values_method=fill_values_method
                )
            )

    def find_references(self, document, fields=None, results=None):
        if results is None:
            results = []

        if not isinstance(document, Document):
            return results

        if fields:
            fields = [
                (field_name, document._fields[field_name])
                for field_name in fields
                if field_name in fields
            ]
        else:
            fields = [field for field in document._fields.items()]

        for field_name, field in fields:
            self.find_reference_field(document, results, field_name, field)
            self.find_list_field(document, results, field_name, field)
            self.find_embed_field(document, results, field_name, field)

        return results

    def _get_load_function(self, document, field_name, document_type):
        """Get appropriate method to load reference field of the document"""
        if field_name in document._reference_loaded_fields:
            # there is a projection for this field
            fields = document._reference_loaded_fields[field_name]
            return document_type.objects.fields(**fields).get
        return document_type.objects.get

    def find_reference_field(self, document, results, field_name, field):
        if self.is_reference_field(field):
            value = document._values.get(field_name, None)
            load_function = self._get_load_function(
                document, field_name, field.reference_type
            )
            if value is not None:
                results.append([
                    load_function,
                    value,
                    document._values,
                    field_name,
                    None
                ])

    def find_list_field(self, document, results, field_name, field):
        from motorengine.fields.reference_field import ReferenceField
        if self.is_list_field(field):
            values = document._values.get(field_name)
            if values:
                document_type = values[0].__class__
                if isinstance(field._base_field, ReferenceField):
                    document_type = field._base_field.reference_type
                    load_function = self._get_load_function(
                        document, field_name, document_type
                    )
                    for value in values:
                        results.append([
                            load_function,
                            value,
                            document._values,
                            field_name,
                            self.fill_list_values_collection
                        ])
                    document._values[field_name] = []
                else:
                    self.find_references(document=document_type, results=results)

    def find_embed_field(self, document, results, field_name, field):
        if self.is_embedded_field(field):
            value = document._values.get(field_name, None)
            if value:
                self.find_references(document=value, results=results)

    def get_field_value(self, name):
        if name not in self._fields:
            raise ValueError("Field %s not found in instance of %s." % (
                name,
                self.__class__.__name__
            ))

        field = self._fields[name]
        value = field.get_value(self._values.get(name, None))

        return value

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            field = self._fields[name]
            is_reference_field = self.is_reference_field(field)
            value = field.get_value(self._values.get(name, None))

            if is_reference_field and value is not None and not isinstance(value, field.reference_type):
                message = "The property '%s' can't be accessed before calling 'load_references'" + \
                    " on its instance first (%s) or setting __lazy__ to False in the %s class."

                raise LoadReferencesRequiredError(
                    message % (name, self.__class__.__name__, self.__class__.__name__)
                )

            return value

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        from motorengine.fields.dynamic_field import DynamicField

        if name not in AUTHORIZED_FIELDS and name not in self._fields:
            self._fields[name] = DynamicField(db_field="_%s" % name)

        if name in self._fields:
            self._values[name] = value
            return

        object.__setattr__(self, name, value)

    @classmethod
    def get_field_by_db_name(cls, name):
        for field_name, field in cls._fields.items():
            if name == field.db_field or name.lstrip("_") == field.db_field:
                return field
        return None

    @classmethod
    def get_fields(cls, name, fields=None):
        from motorengine import EmbeddedDocumentField, ListField
        from motorengine.fields.dynamic_field import DynamicField

        if fields is None:
            fields = []

        if '.' not in name:
            dyn_field = DynamicField(db_field="_%s" % name)
            fields.append(cls._fields.get(name, dyn_field))
            return fields

        field_values = name.split('.')
        dyn_field = DynamicField(db_field="_%s" % field_values[0])
        obj = cls._fields.get(field_values[0], dyn_field)
        fields.append(obj)

        if isinstance(obj, (EmbeddedDocumentField, )):
            obj.embedded_type.get_fields(".".join(field_values[1:]), fields=fields)

        if isinstance(obj, (ListField, )):
            obj.item_type.get_fields(".".join(field_values[1:]), fields=fields)

        return fields


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    '''
    Base class for all documents specified in MotorEngine.
    '''
    pass
