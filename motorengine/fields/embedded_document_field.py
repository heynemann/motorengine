#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.utils import get_class
from motorengine.fields.base_field import BaseField


class EmbeddedDocumentField(BaseField):
    '''
    Field responsible for storing an embedded document.

    Usage:

    .. testcode:: modeling_fields

        class Comment(Document):
            text = StringField(required=True)

        comment = EmbeddedDocumentField(embedded_document_type=Comment)

    Available arguments (apart from those in `BaseField`):

    * `embedded_document_type` - The type of document that this field accepts as an embedded document.
    '''

    def __init__(self, embedded_document_type=None, *args, **kw):
        super(EmbeddedDocumentField, self).__init__(*args, **kw)

        self._embedded_document_type = embedded_document_type
        self._resolved_embedded_type = None

    @property
    def embedded_type(self):
        if self._resolved_embedded_type is None:
            if isinstance(self._embedded_document_type, six.string_types):
                self._resolved_embedded_type = get_class(self._embedded_document_type)
            else:
                self._resolved_embedded_type = self._embedded_document_type

        return self._resolved_embedded_type

    def validate(self, value):
        # avoiding circular reference
        from motorengine import Document

        if not isinstance(self.embedded_type, type) or not issubclass(self.embedded_type, Document):
            raise ValueError(
                "The field 'embedded_document_type' argument must be a subclass of Document, not '%s'." %
                str(self.embedded_type)
            )

        if value is None:
            return True

        if value is not None and not isinstance(value, self.embedded_type):
            return False

        return value.validate()

    def to_son(self, value):
        if value is None:
            return None

        base = dict()

        base.update(value.to_son())

        return base

    def from_son(self, value):
        if value is None:
            return None

        return self.embedded_type.from_son(value)
