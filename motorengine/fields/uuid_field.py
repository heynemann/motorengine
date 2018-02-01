#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import UUID

import six

from motorengine.fields.base_field import BaseField


class UUIDField(BaseField):
    '''
    Field responsible for storing :py:class:`uuid.UUID`.

    Usage:

    .. testcode:: modeling_fields

        name = UUIDField(required=True)
    '''

    def validate(self, value):
        if value is None:
            return True
        if isinstance(value, UUID):
            return True

        if isinstance(value, six.string_types):
            try:
                UUID(value)
                return True
            except ValueError:
                pass

        return False

    def is_empty(self, value):
        return value is None or str(value) == ""

    def to_son(self, value):
        if isinstance(value, six.string_types):
            return UUID(value)

        return value
