#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import BooleanField
from tests import AsyncTestCase


class TestBoolField(AsyncTestCase):
    def test_create_bool_field(self):
        field = BooleanField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_to_son(self):
        field = BooleanField()

        expect(field.to_son(True)).to_equal(1)
        expect(field.to_son(False)).to_equal(0)

    def test_from_son(self):
        field = BooleanField()
        expect(field.from_son(1)).to_equal(True)
        expect(field.from_son(0)).to_equal(False)
