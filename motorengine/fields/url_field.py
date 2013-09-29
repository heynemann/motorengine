#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from motorengine.fields.base_field import BaseField


class URLField(BaseField):
    '''
    Field responsible for storing URLs.

    Usage:

    .. testcode:: modeling_fields

        name = URLField(required=True)

    Available arguments (apart from those in `BaseField`): `None`

    .. note::

        MotorEngine does not implement the `verify_exists` parameter
        as MongoEngine due to async http requiring the current io_loop.
    '''

    URL_REGEX = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    def validate(self, value):
        is_url = URLField.URL_REGEX.match(value)

        return is_url
