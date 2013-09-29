#!/usr/bin/env python
# -*- coding: utf-8 -*-

import decimal

import six

from motorengine.fields.base_field import BaseField


class DecimalField(BaseField):
    '''
    Field responsible for storing fixed-point decimal numbers (:py:class:`decimal.Decimal`).

    Usage:

    .. testcode:: modeling_fields

        import decimal

        name = DecimalField(required=True, min_value=None, max_value=None, precision=2, rounding=decimal.ROUND_HALF_UP)

    Available arguments (apart from those in `BaseField`):

    * `min_value` - Raises a validation error if the decimal being stored is lesser than this value
    * `max_value` - Raises a validation error if the decimal being stored is greather than this value
    * `precision` - Number of decimal places to store.
    * `rounding` - The rounding rule from the python decimal library:

        * decimal.ROUND_CEILING (towards Infinity)
        * decimal.ROUND_DOWN (towards zero)
        * decimal.ROUND_FLOOR (towards -Infinity)
        * decimal.ROUND_HALF_DOWN (to nearest with ties going towards zero)
        * decimal.ROUND_HALF_EVEN (to nearest with ties going to nearest even integer)
        * decimal.ROUND_HALF_UP (to nearest with ties going away from zero)
        * decimal.ROUND_UP (away from zero)
        * decimal.ROUND_05UP (away from zero if last digit after rounding towards zero would have been 0 or 5; otherwise towards zero)

    .. note::

        Decimal field stores the value as a string in MongoDB to preserve the precision.
    '''

    def __init__(self, min_value=None, max_value=None, precision=2, rounding=decimal.ROUND_HALF_UP, *args, **kw):
        super(DecimalField, self).__init__(*args, **kw)
        self.min_value = min_value
        if self.min_value is not None:
            self.min_value = decimal.Decimal(min_value)

        self.max_value = max_value
        if self.max_value is not None:
            self.max_value = decimal.Decimal(max_value)

        self.precision = decimal.Decimal(".%s" % ("0" * precision))
        self.rounding = rounding

    def to_son(self, value):
        value = decimal.Decimal(value)
        return six.u(str(value.quantize(self.precision, rounding=self.rounding)))

    def from_son(self, value):
        value = decimal.Decimal(value)

        return value.quantize(self.precision, rounding=self.rounding)

    def validate(self, value):
        try:
            value = decimal.Decimal(value)
        except:
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True
