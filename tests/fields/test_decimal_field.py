#!/usr/bin/env python
# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_DOWN, ROUND_UP

from preggy import expect

from motorengine import DecimalField
from tests import AsyncTestCase


class TestDecimalField(AsyncTestCase):
    def test_create_decimal_field(self):
        field = DecimalField(db_field="test", min_value=10.5, max_value=200.6)
        expect(field.db_field).to_equal("test")
        expect(field.min_value).to_equal(Decimal(10.5))
        expect(field.max_value).to_equal(Decimal(200.6))

    def test_to_son(self):
        field = DecimalField()

        expect(field.to_son(10.0230)).to_equal(u'10.02')
        expect(field.to_son("10.56823")).to_equal(u'10.57')

    def test_from_son(self):
        field = DecimalField()

        expect(field.from_son(u"10.0230")).to_equal(Decimal("10.02"))
        expect(field.from_son(u"10.56948")).to_equal(Decimal("10.57"))

    def test_validate_enforces_decimals(self):
        field = DecimalField()

        expect(field.validate(1.0)).to_be_true()
        expect(field.validate("1.5")).to_be_true()
        expect(field.validate("qwe")).to_be_false()

    def test_validate_enforces_min_value(self):
        field = DecimalField(min_value=Decimal(5.4))

        expect(field.validate(1)).to_be_false()
        expect(field.validate(5.5)).to_be_true()
        expect(field.validate("5.5")).to_be_true()

    def test_validate_enforces_max_value(self):
        field = DecimalField(max_value=Decimal(5.4))

        expect(field.validate(5.3)).to_be_true()
        expect(field.validate(5.5)).to_be_false()
        expect(field.validate("5.2")).to_be_true()

    def test_to_son_with_different_precision(self):
        field = DecimalField(precision=4)

        expect(field.to_son(10.023423924)).to_equal(u'10.0234')
        expect(field.to_son("10.56823239")).to_equal(u'10.5682')

    def test_to_son_with_different_rounding(self):
        field = DecimalField(precision=4, rounding=ROUND_DOWN)

        expect(field.to_son(10.023493924)).to_equal(u'10.0234')
        expect(field.to_son("10.5682999")).to_equal(u'10.5682')

        field = DecimalField(precision=4, rounding=ROUND_UP)

        expect(field.to_son(10.023493924)).to_equal(u'10.0235')
        expect(field.to_son("10.5682999")).to_equal(u'10.5683')
