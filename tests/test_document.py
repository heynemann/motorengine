#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import (
    Document, StringField, BooleanField, ListField,
    EmbeddedDocumentField, ReferenceField, DESCENDING,
    URLField, DateTimeField
)
from motorengine.errors import InvalidDocumentError, LoadReferencesRequiredError
from tests import AsyncTestCase


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50, default=lambda: "Bernardo")
    last_name = StringField(max_length=50, default="Heynemann")
    is_admin = BooleanField(default=True)
    website = URLField(default="http://google.com/")
    updated_at = DateTimeField(required=True, auto_now_on_insert=True, auto_now_on_update=True)

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
        self.drop_coll("Post")
        self.drop_coll("Comment")
        self.drop_coll("CommentNotLazy")

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

        result = self.wait()

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")

    def test_can_create_new_instance_with_defaults(self):
        user = User(email="heynemann@gmail.com")
        user.save(callback=self.stop)

        result = self.wait()

        expect(result._id).not_to_be_null()
        expect(result.email).to_equal("heynemann@gmail.com")
        expect(result.first_name).to_equal("Bernardo")
        expect(result.last_name).to_equal("Heynemann")
        expect(result.is_admin).to_be_true()

    def test_creating_invalid_instance_fails(self):
        user = User(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", website="bla")
        try:
            user.save(callback=self.stop)
        except InvalidDocumentError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("Field 'website' must be valid.")
        else:
            assert False, "Should not have gotten this far"

        try:
            user = User.objects.create(
                email="heynemann@gmail.com",
                first_name="Bernardo",
                last_name="Heynemann",
                website="bla",
                callback=self.stop
            )
        except InvalidDocumentError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("Field 'website' must be valid.")
        else:
            assert False, "Should not have gotten this far"

    def test_can_create_employee(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)

        result = self.wait()

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

        result = self.wait()

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
        retrieved_user = self.wait()

        expect(retrieved_user._id).to_equal(user._id)
        expect(retrieved_user.email).to_equal("heynemann@gmail.com")
        expect(retrieved_user.first_name).to_equal("Bernardo")
        expect(retrieved_user.last_name).to_equal("Heynemann")
        expect(retrieved_user.emp_number).to_equal("Employee")
        expect(retrieved_user.is_admin).to_be_true()

    def test_after_updated_get_proper_data(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)
        self.wait()

        user.emp_number = "12345"
        user.save(callback=self.stop)
        self.wait()

        Employee.objects.get(user._id, callback=self.stop)
        retrieved_user = self.wait()

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
        users = self.wait()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Someone')
        expect(first_user.last_name).to_equal('Else')
        expect(first_user.email).to_equal("someone@gmail.com")

    def test_can_limit_number_of_documents(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.limit(1).find_all(callback=self.stop)
        users = self.wait()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Bernardo')
        expect(first_user.last_name).to_equal('Heynemann')
        expect(first_user.email).to_equal("heynemann@gmail.com")

    def test_cant_order_for_invalid_field(self):
        try:
            User.objects.order_by("invalid_field")
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("Invalid order by field 'invalid_field': Field not found in 'User'.")
        else:
            assert False, "Should not have gotten this far"

    def test_can_order_documents(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.order_by("first_name", DESCENDING).find_all(callback=self.stop)
        users = self.wait()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(2)

        first_user = users[0]
        expect(first_user.first_name).to_equal('Someone')
        expect(first_user.last_name).to_equal('Else')
        expect(first_user.email).to_equal("someone@gmail.com")

    def test_can_count_documents(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.count(callback=self.stop)
        user_count = self.wait()
        expect(user_count).to_equal(2)

        User.objects.filter(email="someone@gmail.com").count(callback=self.stop)
        user_count = self.wait()
        expect(user_count).to_equal(1)

        User.objects.filter(email="invalid@gmail.com").count(callback=self.stop)
        user_count = self.wait()
        expect(user_count).to_equal(0)

    def test_saving_without_required_fields_raises(self):
        user = Employee(first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        try:
            user.save(callback=self.stop)
        except InvalidDocumentError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of("Field 'email' is required.")

    def test_can_save_and_get_reference_with_lazy(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        Post.objects.create(title="Testing post", body="Testing post body", callback=self.stop)
        post = self.wait()

        comment = Comment(text="Comment text for lazy test", user=user)
        post.comments.append(comment)
        post.save(self.stop)
        self.wait()

        Post.objects.get(post._id, callback=self.stop)
        loaded_post = self.wait()

        loaded_post.load_references(callback=self.stop)
        result = self.wait()

        expect(result['loaded_reference_count']).to_equal(1)

    def test_can_save_and_get_reference_without_lazy(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        comment = CommentNotLazy(text="Comment text", user=user)
        comment.save(callback=self.stop)
        self.wait()

        CommentNotLazy.objects.get(comment._id, callback=self.stop)
        loaded_comment = self.wait()

        expect(loaded_comment).not_to_be_null()
        expect(loaded_comment.user._id).to_equal(user._id)

    def test_can_save_and_retrieve_blog_post(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        Post.objects.create(title="Testing post", body="Testing post body", callback=self.stop)
        post = self.wait()

        post.comments.append(Comment(text="Comment text for blog post", user=user))
        post.save(callback=self.stop)
        self.wait()

        Post.objects.get(post._id, callback=self.stop)
        loaded_post = self.wait()

        expect(loaded_post).not_to_be_null()

        expect(loaded_post._id).to_equal(post._id)
        expect(loaded_post.title).to_equal("Testing post")
        expect(loaded_post.body).to_equal("Testing post body")

        expect(loaded_post.comments).to_length(1)
        expect(loaded_post.comments[0].text).to_equal("Comment text for blog post")

        try:
            loaded_post.comments[0].user
        except LoadReferencesRequiredError:
            err = sys.exc_info()[1]
            expected = "The property 'user' can't be accessed before calling 'load_references' on its instance first (Comment) or setting __lazy__ to False in the Comment class."
            expect(err).to_have_an_error_message_of(expected)
        else:
            assert False, "Should not have gotten this far"

        loaded_post.load_references(callback=self.stop)
        result = self.wait()

        loaded_reference_count = result['loaded_reference_count']
        expect(loaded_reference_count).to_equal(1)

        expect(loaded_post.comments[0].user).to_be_instance_of(User)
        expect(loaded_post.comments[0].user._id).to_equal(user._id)
        expect(loaded_post.comments[0].user.email).to_equal("heynemann@gmail.com")
        expect(loaded_post.comments[0].user.first_name).to_equal("Bernardo")
        expect(loaded_post.comments[0].user.last_name).to_equal("Heynemann")
