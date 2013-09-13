#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class ReferenceField(BaseField):
    def __init__(self, reference_document_type=None, *args, **kw):
        super(ReferenceField, self).__init__(*args, **kw)

        # avoiding circular reference
        from motorengine import Document

        if not isinstance(reference_document_type, type) or not issubclass(reference_document_type, Document):
            raise ValueError("The field 'reference_document_type' argument must be a subclass of Document, not '%s'." % str(reference_document_type))

        self._reference_document_type = reference_document_type

    def validate(self, value):
        if not isinstance(value, self._reference_document_type):
            return False

        return value._id is not None

    def to_son(self, value):
        return value._id

    def from_son(self, value):
        return value
