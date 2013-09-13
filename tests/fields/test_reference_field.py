#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect
from bson.objectid import ObjectId

from motorengine import Document, StringField, ReferenceField
from tests import AsyncTestCase


class User(Document):
    name = StringField()


class TestReferenceField(AsyncTestCase):
    def test_cant_create_reference_field_of_the_wrong_type(self):
        try:
            ReferenceField(reference_document_type="test")
        except ValueError:
            err = sys.exc_info()[1]
            expected = "The field 'reference_document_type' argument must be a subclass of Document, not 'test'."
            expect(err).to_have_an_error_message_of(expected)
        else:
            assert False, "Should not have gotten this far"

    def test_create_reference_field(self):
        field = ReferenceField(db_field="test", reference_document_type=User)
        expect(field.db_field).to_equal("test")
        expect(field._reference_document_type).to_equal(User)

    def test_to_son(self):
        field = ReferenceField(db_field="test", reference_document_type=User)

        u = User(name="test")
        u._id = ObjectId("123456789012123456789012")

        result = field.to_son(u)
        expect(str(result)).to_equal(str(u._id))

    def test_from_son(self):
        field = ReferenceField(db_field="test", reference_document_type=User)

        data = ObjectId("123456789012123456789012")

        result = field.from_son(data)

        expect(result).to_equal(ObjectId("123456789012123456789012"))
