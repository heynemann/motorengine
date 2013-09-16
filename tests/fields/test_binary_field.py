#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
from preggy import expect

from motorengine import BinaryField
from tests import AsyncTestCase


class TestBinaryField(AsyncTestCase):
    def test_create_binary_field(self):
        field = BinaryField(db_field="test", max_bytes=200)
        expect(field.db_field).to_equal("test")
        expect(field.max_bytes).to_equal(200)

    def test_validate_enforces_binary_strings(self):
        field = BinaryField()

        expect(field.validate(1)).to_be_false()
        expect(field.validate(b'abc')).to_be_true()
        expect(field.validate(six.u('abc'))).to_be_false()

    def test_validate_enforces_max_bytes(self):
        field = BinaryField(max_bytes=20)

        expect(field.validate(b"-----")).to_be_true()
        expect(field.validate(b"-----" * 40)).to_be_false()

    def test_is_empty(self):
        field = BinaryField()
        expect(field.is_empty(None)).to_be_true()
        expect(field.is_empty("")).to_be_true()
        expect(field.is_empty("123")).to_be_false()
