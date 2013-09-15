#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from tornado.testing import gen_test

from motorengine import (
    Document, StringField, BooleanField, ListField,
    EmbeddedDocumentField, ReferenceField, DESCENDING
)
from tests import AsyncTestCase


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    is_admin = BooleanField(default=True)

    def __repr__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class Employee(User):
    emp_number = StringField()


class Comment(Document):
    text = StringField(required=True)
    user = ReferenceField(User, required=True)


class CommentNotLazy(Document):
    __lazy__ = False

    text = StringField(required=True)
    user = ReferenceField(User, required=True)


class Post(Document):
    title = StringField(required=True)
    body = StringField(required=True)

    comments = ListField(EmbeddedDocumentField(Comment))


class TestDocument(AsyncTestCase):
    def setUp(self):
        super(TestDocument, self).setUp()
        self.drop_coll("User")
        self.drop_coll("Employee")

    @gen_test
    def test_can_create_new_instance(self):
        user = User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")

        result = yield user.save()

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")

    @gen_test
    def test_can_create_employee(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")

        result = yield user.save()

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")
        expect(result.emp_number).to_equal("Employee")

    @gen_test
    def test_can_update_employee(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.emp_number = "12345"

        result = yield user.save()

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")
        expect(result.emp_number).to_equal("12345")

    @gen_test
    def test_can_get_instance(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        yield user.save()

        retrieved_user = yield Employee.objects.get(user._id)

        expect(retrieved_user._id).to_equal(user._id)
        expect(retrieved_user.email).to_equal("heynemann@gmail.com")
        expect(retrieved_user.first_name).to_equal("Bernardo")
        expect(retrieved_user.last_name).to_equal("Heynemann")
        expect(retrieved_user.emp_number).to_equal("Employee")
        expect(retrieved_user.is_admin).to_be_true()

    @gen_test
    def test_can_find_proper_document(self):
        yield User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        yield User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else")

        users = yield User.objects.filter(email="someone@gmail.com").find_all()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Someone')
        expect(first_user.last_name).to_equal('Else')
        expect(first_user.email).to_equal("someone@gmail.com")

    @gen_test
    def test_can_limit_number_of_documents(self):
        yield User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        yield User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else")

        users = yield User.objects.limit(1).find_all()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Bernardo')
        expect(first_user.last_name).to_equal('Heynemann')
        expect(first_user.email).to_equal("heynemann@gmail.com")

    @gen_test
    def test_can_order_documents(self):
        yield User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        yield User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else")

        users = yield User.objects.order_by("first_name", DESCENDING).find_all()

        expect(users).to_be_instance_of(list)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Someone')
        expect(first_user.last_name).to_equal('Else')
        expect(first_user.email).to_equal("someone@gmail.com")

    @gen_test
    def test_can_count_documents(self):
        yield User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann")
        yield User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else")

        user_count = yield User.objects.count()
        expect(user_count).to_equal(2)

        user_count = yield User.objects.filter(first_name="Bernardo").count()
        expect(user_count).to_equal(1)

        user_count = yield User.objects.filter(email="invalid@gmail.com").count()
        expect(user_count).to_equal(0)

    @gen_test
    def test_can_save_and_get_reference_without_lazy(self):
        user = yield User.objects.create(
            email="heynemann@gmail.com",
            first_name="Bernardo",
            last_name="Heynemann"
        )

        comment = yield CommentNotLazy(text="Comment text", user=user).save()

        loaded_comment = yield CommentNotLazy.objects.get(comment._id)

        expect(loaded_comment).not_to_be_null()
        expect(loaded_comment.user._id).to_equal(user._id)
