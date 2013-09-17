#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.fields.base_field import BaseField
from motorengine.utils import get_class


class ReferenceField(BaseField):
    def __init__(self, reference_document_type=None, *args, **kw):
        super(ReferenceField, self).__init__(*args, **kw)

        self._reference_document_type = reference_document_type
        self._resolved_reference_type = None

    @property
    def reference_type(self):
        if self._resolved_reference_type is None:
            if isinstance(self._reference_document_type, six.string_types):
                self._resolved_reference_type = get_class(self._reference_document_type)
            else:
                self._resolved_reference_type = self._reference_document_type

        return self._resolved_reference_type

    def validate(self, value):
        # avoiding circular reference
        from motorengine import Document

        if not isinstance(self.reference_type, type) or not issubclass(self.reference_type, Document):
            raise ValueError("The field 'reference_document_type' argument must be a subclass of Document, not '%s'." % str(self.reference_type))

        if value is not None and not isinstance(value, self.reference_type):
            return False

        return value is None or value._id is not None

    def to_son(self, value):
        if value is None:
            return None

        return value._id

    def from_son(self, value):
        return value
