#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import Document
from motorengine.fields.dynamic_field import DynamicField
from tests import AsyncTestCase


class TestDynamicField(AsyncTestCase):
    def test_create_dynamic_field(self):
        # we need a document to verify document's metaclass accepts the field
        class TestDocument(Document):
            dynamic_field = DynamicField(db_field="_test_something_name")

        test_document = TestDocument()

        expect(test_document.dynamic_field.db_field).to_equal("_test_something_name")
        expect(test_document.dynamic_field.name).to_equal("test_something_name")
