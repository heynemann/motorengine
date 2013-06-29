#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import UUID

import six

from motorengine.fields.base_field import BaseField


class UUIDField(BaseField):
    def validate(self, value):
        if isinstance(value, UUID):
            return True

        if isinstance(value, six.string_types):
            try:
                UUID(value)
                return True
            except TypeError:
                return False
            except ValueError:
                return False

        return False

    def is_empty(self, value):
        return value is None or str(value) == ""
