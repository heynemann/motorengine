#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import re

from motorengine.fields.base_field import BaseField


class EmailField(BaseField):
    '''
    Field responsible for storing e-mail addresses.

    Usage:

    .. testcode:: modeling_fields

        name = EmailField(required=True)

    Available arguments (apart from those in `BaseField`): `None`
    '''

    EMAIL_REGEX = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE  # domain
    )

    def validate(self, value):
        if value is None:
            return True

        is_email = EmailField.EMAIL_REGEX.match(value)
        return is_email
