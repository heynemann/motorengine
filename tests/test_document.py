#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import connect, disconnect, Document, StringField
from tests import AsyncTestCase


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class Employee(User):
    emp_number = StringField()


class TestDocument(AsyncTestCase):
    def setUp(self):
        super(TestDocument, self).setUp()
        connect("test", host="localhost", port=4445, io_loop=self.io_loop)

    def tearDown(self):
        super(TestDocument, self).tearDown()
        disconnect()

    def test_has_proper_collection(self):
        assert User.__collection__ == 'User'

    def test_setting_invalid_property_raises(self):
        try:
            User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", wrong_property="value")
        except ValueError:
            err = sys.exc_info()
            expect(err[1]).to_have_an_error_message_of("Error creating document User: Invalid property 'wrong_property'.")
        else:
            assert False, "Should not have gotten this far"

    def test_can_create_new_instance(self):
        user = User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        user.save(callback=self.stop)

        result = self.wait()['kwargs']['instance']

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")

    def test_can_create_employee(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)

        result = self.wait()['kwargs']['instance']

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")
        expect(result.emp_number).to_equal("Employee")
