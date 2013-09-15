#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from datetime import datetime

from motorengine import DateTimeField
from tests import AsyncTestCase


class TestDateTimeField(AsyncTestCase):
    def test_create_datetime_field(self):
        field = DateTimeField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_to_son(self):
        field = DateTimeField()

        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.to_son(dt)).to_equal(dt)

    def test_from_son(self):
        field = DateTimeField()

        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.from_son(dt)).to_equal(dt)

    def test_to_son_from_string(self):
        field = DateTimeField()

        dt_str = "2010-11-12 13:14:15"
        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.to_son(dt_str)).to_equal(dt)

    def test_from_son_from_string(self):
        field = DateTimeField()

        dt_str = "2010-11-12 13:14:15"
        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.from_son(dt_str)).to_equal(dt)
