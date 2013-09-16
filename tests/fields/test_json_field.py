#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import calendar

from preggy import expect

from motorengine import JsonField
from motorengine.fields.json_field import serialize
from tests import AsyncTestCase


class TestJsonField(AsyncTestCase):
    def test_create_json_field(self):
        field = JsonField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate_enforces_jsonifiable_objects(self):
        field = JsonField(db_field="test")

        expect(field.validate(1)).to_be_true()
        expect(field.validate([1, 2, 3])).to_be_true()
        expect(field.validate({"a": 1, "b": 3})).to_be_true()

    def test_to_son(self):
        dt = datetime(2010, 11, 12, 13, 14, 15)

        field = JsonField(db_field="test")

        expect(field.to_son(1)).to_equal(serialize(1))
        expect(field.to_son([1, 2, 3])).to_equal(serialize([1, 2, 3]))
        expect(field.to_son({"a": 1, "b": 3})).to_equal(serialize({"a": 1, "b": 3}))
        expect(field.to_son(dt)).to_equal(serialize(dt))

    def test_from_son(self):
        dt = datetime.utcnow()

        field = JsonField(db_field="test")

        expect(field.from_son("1")).to_equal(1)
        expect(field.from_son("[1, 2, 3]")).to_be_like([1, 2, 3])
        expect(field.from_son('{"a": 1, "b": 3}')).to_be_like({"a": 1, "b": 3})

        try:
            import ujson  # NOQA
            dt_value = calendar.timegm(dt.utctimetuple())
            expect(field.from_son(serialize(dt))).to_be_like(dt_value)
        except ImportError:
            value = field.from_son(serialize(dt)).isoformat()
            expect(value[:20]).to_equal(dt.isoformat()[:20])
