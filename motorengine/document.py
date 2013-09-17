#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
from tornado.concurrent import return_future

from motorengine.metaclasses import DocumentMetaClass
from motorengine.errors import InvalidDocumentError, LoadReferencesRequiredError


AUTHORIZED_FIELDS = ['_id', '_values']


class BaseDocument(object):
    def __init__(self, *args, **kw):
        self._id = kw.pop('_id', None)
        self._values = {}

        for key, field in self._fields.items():
            if callable(field.default):
                self._values[key] = field.default()
            else:
                self._values[key] = field.default

        for key, value in kw.items():
            if key not in self._db_field_map:
                raise ValueError("Error creating document %s: Invalid property '%s'." % (
                    self.__class__.__name__, key
                ))
            self._values[key] = value

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
    def from_son(cls, dic):
        field_values = {}
        for name, value in dic.items():
            if name in cls._fields:
                field_values[name] = cls._fields[name].from_son(value)
            else:
                field_values[name] = value

        return cls(**field_values)

    def to_son(self):
        data = dict()

        for name, value in self._values.items():
            data[name] = self._fields[name].to_son(value)

        return data

    def validate(self):
        return self.validate_fields()

    def validate_fields(self):
        for name, field in self._fields.items():
            value = self._values[field.db_field]
            if field.required and field.is_empty(value):
                raise InvalidDocumentError("Field '%s' is required." % name)
            if not field.validate(value):
                raise InvalidDocumentError("Field '%s' must be valid." % name)

        return True

    @return_future
    def save(self, callback, alias=None):
        '''
        Saves a new instance of this document.

        Usage::

            doc = MyDocument(some_property="value")
            doc.save(callback)

            def callback(instance):
                # do something with instance
        '''
        self.objects.save(self, callback=callback, alias=alias)

    def handle_load_reference(self, callback, references, reference_count, values_collection, field_name):
        def handle(*args, **kw):
            values_collection[field_name] = args[0]
            references.pop()

            if len(references) == 0:
                callback({
                    'loaded_reference_count': reference_count,
                    'loaded_values': values_collection
                })

        return handle

    @return_future
    def load_references(self, callback, alias=None):
        references = self.find_references(self)
        reference_count = len(references)
        for dereference_function, document_id, values_collection, field_name in references:
            dereference_function(
                document_id,
                callback=self.handle_load_reference(
                    callback=callback,
                    references=references,
                    reference_count=reference_count,
                    values_collection=values_collection,
                    field_name=field_name
                )
            )

    def find_references(self, document, results=[]):
        for field_name, field in document._fields.items():
            self.find_reference_field(document, results, field_name, field)
            self.find_list_field(document, results, field_name, field)
            self.find_embed_field(document, results, field_name, field)

        return results

    def find_reference_field(self, document, results, field_name, field):
        if self.is_reference_field(field):
            value = document._values.get(field_name, None)
            if value is not None:
                results.append([
                    field._reference_document_type.objects.get,
                    value,
                    document._values,
                    field_name
                ])

    def find_list_field(self, document, results, field_name, field):
        if self.is_list_field(field):
            for value in document._values[field_name]:
                if value:
                    self.find_references(value, results)

    def find_embed_field(self, document, results, field_name, field):
        if self.is_embedded_field(field):
            value = document._values.get(field_name, None)
            if value:
                self.find_references(value, results)

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            field = self._fields[name]
            is_reference_field = self.is_reference_field(field)
            value = field.get_value(self._values.get(name, None))

            if is_reference_field and not isinstance(value, field._reference_document_type):
                message = "The property '%s' can't be accessed before calling 'load_references'" + \
                    " on its instance first (%s) or setting __lazy__ to False in the %s class."

                raise LoadReferencesRequiredError(
                    message % (name, self.__class__.__name__, self.__class__.__name__)
                )

            return value

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name not in AUTHORIZED_FIELDS and name not in self._fields:
            raise ValueError("Error updating property: Invalid property '%s'." % name)

        if name in self._fields:
            self._values[name] = self._fields[name].get_value(value)
            return

        object.__setattr__(self, name, value)


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    '''
    Base class for all documents specified in MotorEngine.
    '''
    pass
