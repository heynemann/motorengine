#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import Document, StringField
from motorengine.errors import InvalidDocumentError
from tests import AsyncTestCase


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    def __repr__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class Employee(User):
    emp_number = StringField()


class TestDocument(AsyncTestCase):
    def setUp(self):
        super(TestDocument, self).setUp()
        self.drop_coll("User")
        self.drop_coll("Employee")

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

        user = User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        try:
            user.invalid_property = "a"
        except ValueError:
            err = sys.exc_info()
            expect(err[1]).to_have_an_error_message_of("Error updating property: Invalid property 'invalid_property'.")
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

    def test_duplicate_fields(self):
        try:
            class DuplicateField(User):
                email = StringField(required=True)
        except InvalidDocumentError:
            e = sys.exc_info()[1]
            expect(e).to_have_an_error_message_of("Multiple db_fields defined for: email ")
        else:
            assert False, "Should not have gotten this far."

    def test_can_update_employee(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.emp_number = "12345"
        user.save(callback=self.stop)

        result = self.wait()['kwargs']['instance']

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")
        expect(result.emp_number).to_equal("12345")

    def test_can_get_instance(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)
        self.wait()

        Employee.objects.get(user._id, callback=self.stop)
        retrieved_user = self.wait()['kwargs']['instance']

        expect(retrieved_user._id).to_equal(user._id)
        expect(retrieved_user.email).to_equal("heynemann@gmail.com")
        expect(retrieved_user.first_name).to_equal("Bernardo")
        expect(retrieved_user.last_name).to_equal("Heynemann")
        expect(retrieved_user.emp_number).to_equal("Employee")

    def test_after_updated_get_proper_data(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)
        self.wait()

        user.emp_number = "12345"
        user.save(callback=self.stop)
        self.wait()

        Employee.objects.get(user._id, callback=self.stop)
        retrieved_user = self.wait()['kwargs']['instance']

        expect(retrieved_user._id).to_equal(user._id)
        expect(retrieved_user.email).to_equal("heynemann@gmail.com")
        expect(retrieved_user.first_name).to_equal("Bernardo")
        expect(retrieved_user.last_name).to_equal("Heynemann")
        expect(retrieved_user.emp_number).to_equal("12345")

    def test_cant_filter_for_invalid_field(self):
        try:
            User.objects.filter(invalid_field=True)
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("Invalid filter 'invalid_field': Field not found in 'User'.")
        else:
            assert False, "Should not have gotten this far"

    def test_can_find_proper_document(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.filter(email="someone@gmail.com").find_all(callback=self.stop)
        users = self.wait()['kwargs']['result']

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Someone')
        expect(first_user.last_name).to_equal('Else')
        expect(first_user.email).to_equal("someone@gmail.com")
