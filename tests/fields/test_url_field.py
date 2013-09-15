#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import URLField
from tests import AsyncTestCase


class TestURLField(AsyncTestCase):
    def test_create_url_field(self):
        field = URLField(db_field="test", required=True)
        expect(field.db_field).to_equal("test")
        expect(field.required).to_be_true()

    def test_validate_enforces_URLs(self):
        field = URLField()

        expect(field.validate("some non url")).to_be_false()
        expect(field.validate("http://www.globo.com/")).to_be_true()
