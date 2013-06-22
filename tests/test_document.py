#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import connect, disconnect, Document, StringField
from tests import AsyncTestCase


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class TestDocument(AsyncTestCase):
    def setUp(self):
        super(TestDocument, self).setUp()
        connect("test", host="localhost", port=4445, io_loop=self.io_loop)

    def tearDown(self):
        super(TestDocument, self).tearDown()
        disconnect()

    def test_has_proper_collection(self):
        assert User.__collection__ == 'User'

    def test_can_create_new_instance(self):
        user = User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        user.save(callback=self.stop)

        result = self.wait()

        expect(user._id).not_to_be_null()
        expect(user.email).to_equal("heynemann@gmail.com")
        expect(user.first_name).to_equal("Bernardo")
        expect(user.last_name).to_equal("Heynemann")
