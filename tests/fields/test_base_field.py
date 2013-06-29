#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import BaseField
from tests import AsyncTestCase


class TestBaseField(AsyncTestCase):
    def setUp(self):
        super(TestBaseField, self).setUp()
        BaseField.total_creation_counter = 0

    def test_base_creation_counter(self):
        expect(BaseField.total_creation_counter).to_equal(0)
        BaseField()
        expect(BaseField.total_creation_counter).to_equal(1)
        BaseField()
        expect(BaseField.total_creation_counter).to_equal(2)

    def test_base_db_field(self):
        field = BaseField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_base_required(self):
        field = BaseField()
        expect(field.required).to_be_false()

        field = BaseField(required=True)
        expect(field.required).to_be_true()

    def test_base_default(self):
        field = BaseField()
        expect(field.default).to_be_null()

        field = BaseField(default=True)
        expect(field.default).to_be_true()

    def test_base_is_empty(self):
        field = BaseField()
        expect(field.is_empty(None)).to_be_true()
        expect(field.is_empty(True)).to_be_false()
        expect(field.is_empty(False)).to_be_false()
        expect(field.is_empty("")).to_be_false()
        expect(field.is_empty(20)).to_be_false()

    def test_base_field_to_son(self):
        field = BaseField()

        expect(field.to_son(1)).to_equal(1)
        expect(field.from_son(1)).to_equal(1)

    def test_validate(self):
        field = BaseField()
        expect(field.validate(1)).to_be_true()
