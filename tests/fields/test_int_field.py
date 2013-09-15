#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import IntField
from tests import AsyncTestCase


class TestIntField(AsyncTestCase):
    def test_create_int_field(self):
        field = IntField(db_field="test", min_value=10, max_value=200)
        expect(field.db_field).to_equal("test")
        expect(field.min_value).to_equal(10)
        expect(field.max_value).to_equal(200)

    def test_to_son(self):
        field = IntField()

        expect(field.to_son(10)).to_equal(10)
        expect(field.to_son(10.0)).to_equal(10)
        expect(field.to_son(10.0230)).to_equal(10)
        expect(field.to_son("10")).to_equal(10)

    def test_from_son(self):
        field = IntField()

        expect(field.from_son(10)).to_equal(10)
        expect(field.from_son(10.0)).to_equal(10)
        expect(field.from_son(10.0230)).to_equal(10)
        expect(field.from_son("10")).to_equal(10)

    def test_validate_enforces_integers(self):
        field = IntField()

        expect(field.validate(1)).to_be_true()
        expect(field.validate("1")).to_be_true()
        expect(field.validate("qwe")).to_be_false()

    def test_validate_enforces_min_value(self):
        field = IntField(min_value=5)

        expect(field.validate(1)).to_be_false()
        expect(field.validate(6)).to_be_true()
        expect(field.validate("6")).to_be_true()

    def test_validate_enforces_max_value(self):
        field = IntField(max_value=5)

        expect(field.validate(1)).to_be_true()
        expect(field.validate(6)).to_be_false()
        expect(field.validate("1")).to_be_true()
