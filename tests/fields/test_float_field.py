#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import FloatField
from tests import AsyncTestCase


class TestFloatField(AsyncTestCase):
    def test_create_float_field(self):
        field = FloatField(db_field="test", min_value=10.5, max_value=200.6)
        expect(field.db_field).to_equal("test")
        expect(field.min_value).to_equal(10.5)
        expect(field.max_value).to_equal(200.6)

    def test_to_son(self):
        field = FloatField()

        expect(field.to_son(10.0230)).to_equal(10.023)
        expect(field.to_son("10.56")).to_equal(10.56)

    def test_from_son(self):
        field = FloatField()

        expect(field.from_son(10.0230)).to_equal(10.023)
        expect(field.from_son("10.56")).to_equal(10.56)

    def test_validate_enforces_floats(self):
        field = FloatField()

        expect(field.validate(1.0)).to_be_true()
        expect(field.validate("1.5")).to_be_true()
        expect(field.validate("qwe")).to_be_false()

    def test_validate_enforces_min_value(self):
        field = FloatField(min_value=5.4)

        expect(field.validate(1)).to_be_false()
        expect(field.validate(5.5)).to_be_true()
        expect(field.validate("5.5")).to_be_true()

    def test_validate_enforces_max_value(self):
        field = FloatField(max_value=5.4)

        expect(field.validate(5.3)).to_be_true()
        expect(field.validate(5.5)).to_be_false()
        expect(field.validate("5.2")).to_be_true()
