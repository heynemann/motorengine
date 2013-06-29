#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import StringField
from tests import AsyncTestCase


class TestStringField(AsyncTestCase):
    def test_create_string_field(self):
        field = StringField(db_field="test", max_length=200)
        expect(field.db_field).to_equal("test")
        expect(field.max_length).to_equal(200)

    def test_validate_enforces_strings(self):
        field = StringField(max_length=5)

        expect(field.validate(1)).to_be_false()

    def test_validate_enforces_maxlength(self):
        field = StringField(max_length=5)

        expect(field.validate("-----")).to_be_true()
        expect(field.validate("-----" * 2)).to_be_false()

    def test_is_empty(self):
        field = StringField()
        expect(field.is_empty(None)).to_be_true()
        expect(field.is_empty("")).to_be_true()
        expect(field.is_empty("123")).to_be_false()
