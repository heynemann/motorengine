#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from datetime import datetime, tzinfo, timedelta

from motorengine import DateTimeField
from tests import AsyncTestCase


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)

utc = UTC()


class TestDateTimeField(AsyncTestCase):
    def test_create_datetime_field(self):
        field = DateTimeField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_to_son(self):
        field = DateTimeField()

        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.to_son(dt)).to_equal(dt)
        expect(field.to_son(None)).to_be_null()

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

    def test_from_son_from_string_utc_enforced(self):
        field = DateTimeField(tz=utc)

        dt_str = "2010-11-12 13:14:15"
        dt_utc = datetime(2010, 11, 12, 13, 14, 15, tzinfo=utc)

        expect(field.from_son(dt_str)).to_equal(dt_utc)

    def test_to_son_with_auto_insert(self):
        dt = datetime.now()
        field = DateTimeField(auto_now_on_insert=True)

        expect(field.to_son(field.get_value(None))).to_be_greater_or_equal_to(dt)
        expect(field.get_value(None).tzinfo).to_equal(None)

    def test_to_son_with_auto_insert_utc(self):
        dt = datetime.now(utc)
        field = DateTimeField(auto_now_on_insert=True, tz=utc)

        expect(field.to_son(field.get_value(None))).to_be_greater_or_equal_to(dt)
        expect(field.get_value(None).tzinfo).to_equal(utc)

    def test_to_son_with_auto_insert_and_given_value(self):
        field = DateTimeField(auto_now_on_insert=True)
        dt = datetime(2010, 11, 12, 13, 14, 15)
        expect(field.to_son(field.get_value(dt))).to_equal(dt)
        expect(field.get_value(None).tzinfo).to_equal(None)

    def test_to_son_with_auto_insert_and_given_value_utc(self):
        field = DateTimeField(auto_now_on_insert=True, tz=utc)
        dt = datetime(2010, 11, 12, 13, 14, 15)
        dt_utc = dt.replace(tzinfo=utc)
        expect(field.to_son(field.get_value(dt))).to_equal(dt_utc)

    def test_to_son_with_auto_update(self):
        dt = datetime(2010, 11, 12, 13, 14, 15)
        now = datetime.now()
        field = DateTimeField(auto_now_on_update=True)
        expect(field.get_value(None).tzinfo).to_equal(None)

        expect(field.to_son(field.get_value(dt))).to_be_greater_or_equal_to(now)

    def test_to_son_with_auto_update_utc(self):
        dt = datetime(2010, 11, 12, 13, 14, 15, tzinfo=utc)
        now = datetime.now(utc)
        field = DateTimeField(auto_now_on_update=True, tz=utc)

        expect(field.to_son(field.get_value(dt))).to_be_greater_or_equal_to(now)
        expect(field.get_value(None).tzinfo).to_equal(utc)

    def test_validate(self):
        dt = datetime(2010, 11, 12, 13, 14, 15)
        field = DateTimeField()

        expect(field.validate(None)).to_be_true()
        expect(field.validate(dt)).to_be_true()
        expect(field.validate("qwieiqw")).to_be_false()
