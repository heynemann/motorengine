#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import Document, StringField, EmbeddedDocumentField
from tests import AsyncTestCase


class User(Document):
    name = StringField()


class TestEmbeddedDocumentField(AsyncTestCase):
    def test_cant_create_embedded_field_of_wrong_embedded_type(self):
        try:
            EmbeddedDocumentField(embedded_document_type="test")
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("The field 'embedded_document_type' argument must be a subclass of Document, not 'test'.")
        else:
            assert False, "Should not have gotten this far"

    def test_create_embedded_document_field(self):
        field = EmbeddedDocumentField(db_field="test", embedded_document_type=User)
        expect(field.db_field).to_equal("test")
        expect(field._embedded_document_type).to_equal(User)

    def test_to_son(self):
        field = EmbeddedDocumentField(db_field="test", embedded_document_type=User)

        u = User(name="test")

        expect(field.to_son(u)).to_be_like({
            'name': 'test'
        })

    def test_from_son(self):
        field = EmbeddedDocumentField(db_field="test", embedded_document_type=User)

        user = field.from_son({
            'name': 'test2'
        })

        expect(user).to_be_instance_of(User)
        expect(user.name).to_equal("test2")
