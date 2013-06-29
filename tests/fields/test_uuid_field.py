#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4

from preggy import expect

from motorengine import UUIDField
from tests import AsyncTestCase


class TestUUIDField(AsyncTestCase):
    def test_create_uuid_field(self):
        field = UUIDField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate_enforces_uuid(self):
        field = UUIDField()
        uuid = uuid4()

        expect(field.validate("123")).to_be_false()
        expect(field.validate(uuid)).to_be_true()
        expect(field.validate(str(uuid))).to_be_true()
