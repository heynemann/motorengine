#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import ListField, StringField
from tests import AsyncTestCase


class TestListField(AsyncTestCase):
    def test_create_list_field(self):
        field = ListField(StringField(), db_field="test")
        expect(field.db_field).to_equal("test")
        expect(field._base_field).to_be_instance_of(StringField)

    def test_base_field_must_be_a_field(self):
        try:
            ListField("invalid", db_field="test")
        except ValueError:
            err = sys.exc_info()[1]
            expect(err) \
                .to_have_an_error_message_of("The list field 'field' argument must be an instance of BaseField, not 'invalid'.")
        else:
            assert False, "Should not have gotten this far"

    def test_to_son(self):
        field = ListField(StringField())

        expect(field.to_son([])).to_equal([])
        expect(field.to_son(["1", "2", "3"])).to_equal(["1", "2", "3"])

    def test_from_son(self):
        field = ListField(StringField())

        expect(field.from_son([])).to_equal([])
        expect(field.from_son(["1", "2", "3"])).to_equal(["1", "2", "3"])

    def test_validate_propagates(self):
        field = ListField(StringField())

        expect(field.validate(["1", "2", "3"])).to_be_true()
        expect(field.validate(["1", 2, "3"])).to_be_false()
