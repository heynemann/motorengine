#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField
from motorengine.utils import get_class


class EmbeddedDocumentField(BaseField):
    def __init__(self, embedded_document_type=None, *args, **kw):
        super(EmbeddedDocumentField, self).__init__(*args, **kw)

        # avoiding circular reference
        from motorengine import Document

        if not isinstance(embedded_document_type, type) or not issubclass(embedded_document_type, Document):
            raise ValueError("The field 'embedded_document_type' argument must be a subclass of Document, not '%s'." % str(embedded_document_type))

        self._embedded_document_type = embedded_document_type

    def validate(self, value):
        if not isinstance(value, self._embedded_document_type):
            return False

        return self._embedded_document_type.validate(value)

    def to_son(self, value):
        base = {
            '__module__': value.__module__,
            '__class__': value.__class__.__name__
        }

        base.update(value.to_son())

        return base

    def from_son(self, value):
        module_name = value.pop('__module__')
        klass_name = value.pop('__class__')

        klass = get_class(module_name, klass_name)

        return klass(**value)
