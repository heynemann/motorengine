#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from bson.objectid import ObjectId

from motorengine import ObjectIdField
from tests import AsyncTestCase


class TestObjectIdField(AsyncTestCase):
    def test_create_objectid_field(self):
        field = ObjectIdField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate(self):
        objectid = ObjectId()
        field = ObjectIdField()

        expect(field.validate(None)).to_be_true()
        expect(field.validate(objectid)).to_be_true()
        expect(field.validate("qwe")).to_be_false()
