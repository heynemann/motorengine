#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from uuid import uuid4
from datetime import datetime

from preggy import expect
from tornado.testing import gen_test

from motorengine import (
    Document, StringField, BooleanField, ListField,
    EmbeddedDocumentField, ReferenceField, DESCENDING,
    URLField, DateTimeField, UUIDField, IntField, JsonField
)
from motorengine.errors import InvalidDocumentError, LoadReferencesRequiredError, UniqueKeyViolationError
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

    def test_can_get_instance_with_id_string(self):
        user = Employee(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", emp_number="Employee")
        user.save(callback=self.stop)
        self.wait()

        Employee.objects.get(str(user._id), callback=self.stop)
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

    def test_can_find_with_multiple_filters(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="other@gmail.com", first_name="Bernardo", last_name="Silva", callback=self.stop)
        last_user = self.wait()

        User.objects.filter(first_name="Bernardo").filter_not(email="someone@gmail.com").find_all(callback=self.stop)
        users = self.wait()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(2)

        first_user = users[0]
        expect(first_user.first_name).to_equal(user.first_name)
        expect(first_user.last_name).to_equal(user.last_name)
        expect(first_user.email).to_equal(user.email)

        User.objects.filter(last_name="Silva").filter(first_name="Bernardo").find_all(callback=self.stop)
        users = self.wait()

        expect(users).to_be_instance_of(list)
        expect(users).to_length(1)
        expect(users[0]._id).to_equal(last_user._id)

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

    def test_can_order_documents_by_actual_field(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        self.wait()

        User.objects.create(email="someone@gmail.com", first_name="Someone", last_name="Else", callback=self.stop)
        self.wait()

        User.objects.order_by(User.first_name, DESCENDING).find_all(callback=self.stop)
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

        loaded_post.comments[0].load_references(callback=self.stop)
        result = self.wait()

        expect(result['loaded_reference_count']).to_equal(1)

    def test_can_save_and_get_specific_reference_with_lazy(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        class ReferenceFieldClass(Document):
            ref1 = ReferenceField(User)
            ref2 = ReferenceField(User)
            ref3 = ReferenceField(User)

        ReferenceFieldClass.objects.create(ref1=user, ref2=user, ref3=user, callback=self.stop)
        ref = self.wait()

        ReferenceFieldClass.objects.get(ref._id, callback=self.stop)
        loaded_ref = self.wait()

        loaded_ref.load_references(fields=['ref1'], callback=self.stop)
        result = self.wait()

        expect(result['loaded_reference_count']).to_equal(1)
        expect(loaded_ref.ref1._id).to_equal(user._id)

        try:
            assert loaded_ref.ref2._id
        except LoadReferencesRequiredError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of(
                "The property 'ref2' can't be accessed before calling 'load_references' on its instance first "
                "(ReferenceFieldClass) or setting __lazy__ to False in the ReferenceFieldClass class."
            )
        else:
            assert False, "Should not have gotten this far"

    def test_can_save_and_get_reference_with_find_all(self):
        User.objects.create(email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann", callback=self.stop)
        user = self.wait()

        class ReferenceFieldClass(Document):
            __collection__ = "TestFindAllReferenceField"
            ref1 = ReferenceField(User)
            num = IntField(default=10)

        ReferenceFieldClass.objects.delete(callback=self.stop)
        self.wait()

        ReferenceFieldClass.objects.create(ref1=user, callback=self.stop)
        self.wait()

        ReferenceFieldClass.objects.create(ref1=user, callback=self.stop)
        self.wait()

        ReferenceFieldClass.objects.create(ref1=user, callback=self.stop)
        self.wait()

        ReferenceFieldClass.objects.find_all(lazy=False, callback=self.stop)
        result = self.wait()

        expect(result).to_length(3)
        expect(result[0].ref1._id).to_equal(user._id)

        ReferenceFieldClass.objects.filter(num=20).find_all(lazy=False, callback=self.stop)
        result = self.wait()

        expect(result).to_length(0)

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

        CommentNotLazy.objects.find_all(callback=self.stop)
        loaded_comments = self.wait()

        expect(loaded_comments).to_length(1)
        expect(loaded_comments[0].user._id).to_equal(user._id)

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
            expected = "The property 'user' can't be accessed before calling 'load_references' " + \
                "on its instance first (Comment) or setting __lazy__ to False in the Comment class."
            expect(err).to_have_an_error_message_of(expected)
        else:
            assert False, "Should not have gotten this far"

        loaded_post.comments[0].load_references(callback=self.stop)
        result = self.wait()

        loaded_reference_count = result['loaded_reference_count']
        expect(loaded_reference_count).to_equal(1)

        expect(loaded_post.comments[0].user).to_be_instance_of(User)
        expect(loaded_post.comments[0].user._id).to_equal(user._id)
        expect(loaded_post.comments[0].user.email).to_equal("heynemann@gmail.com")
        expect(loaded_post.comments[0].user.first_name).to_equal("Bernardo")
        expect(loaded_post.comments[0].user.last_name).to_equal("Heynemann")

    def test_saving_a_loaded_post_updates_the_post(self):
        class LoadedPost(Document):
            uuid = UUIDField(default=uuid4)

        uuid = uuid4()

        LoadedPost.objects.create(uuid=uuid, callback=self.stop)
        post = self.wait()

        post.save(callback=self.stop)
        saved_post = self.wait()

        LoadedPost.objects.filter(uuid=uuid).find_all(callback=self.stop)
        posts = self.wait()

        expect(posts).to_length(1)
        expect(posts[0]._id).to_equal(post._id)
        expect(posts[0]._id).to_equal(saved_post._id)

    def test_saving_uses_default(self):
        class LoadedPost(Document):
            uuid = UUIDField(default=uuid4)

        LoadedPost.objects.create(callback=self.stop)
        post = self.wait()

        expect(post.uuid).not_to_be_null()

    def test_getting_by_field(self):
        class LoadedPost(Document):
            uuid = UUIDField(default=uuid4)

        uuid = uuid4()

        LoadedPost.objects.create(uuid=uuid, callback=self.stop)
        post = self.wait()

        LoadedPost.objects.get(uuid=str(uuid), callback=self.stop)
        loaded_post = self.wait()

        expect(loaded_post).not_to_be_null()
        expect(loaded_post._id).to_equal(post._id)

    def test_querying_by_invalid_operator(self):
        try:
            User.objects.filter(email__invalid="test")
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of(
                "Invalid filter 'email__invalid': Invalid operator (if this is a sub-property, "
                "then it must be used in embedded document fields)."
            )
        else:
            assert False, "Should not have gotten this far"

    def test_querying_by_lower_than(self):
        class Test(Document):
            __collection__ = "LowerThan"
            test = IntField()

        Test.objects.delete(callback=self.stop)
        self.wait()

        Test.objects.create(test=10, callback=self.stop)
        test = self.wait()

        Test.objects.create(test=15, callback=self.stop)
        self.wait()

        Test.objects.filter(test__lt=12).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test._id)

        Test.objects.get(test__lt=12, callback=self.stop)
        loaded_test = self.wait()

        expect(loaded_test).not_to_be_null()
        expect(loaded_test._id).to_equal(test._id)

    def test_querying_by_greater_than(self):
        class Test(Document):
            __collection__ = "GreaterThan"
            test = IntField()

        Test.objects.delete(callback=self.stop)
        self.wait()

        Test.objects.create(test=10, callback=self.stop)
        self.wait()

        Test.objects.create(test=15, callback=self.stop)
        test = self.wait()

        Test.objects.filter(test__gt=12).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test._id)

        Test.objects.get(test__gt=12, callback=self.stop)
        loaded_test = self.wait()

        expect(loaded_test).not_to_be_null()
        expect(loaded_test._id).to_equal(test._id)

    def test_querying_by_greater_than_or_equal(self):
        class Test(Document):
            __collection__ = "GreaterThanOrEqual"
            test = IntField()

        Test.objects.delete(callback=self.stop)
        self.wait()

        Test.objects.create(test=10, callback=self.stop)
        test = self.wait()

        Test.objects.create(test=15, callback=self.stop)
        test2 = self.wait()

        Test.objects.filter(test__gte=12).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test2._id)

        Test.objects.filter(test__gte=10).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(2)
        expect(loaded_tests[0]._id).to_equal(test._id)
        expect(loaded_tests[1]._id).to_equal(test2._id)

    def test_querying_by_lesser_than_or_equal(self):
        class Test(Document):
            __collection__ = "LesserThanOrEqual"
            test = IntField()

        Test.objects.delete(callback=self.stop)
        self.wait()

        Test.objects.create(test=10, callback=self.stop)
        test = self.wait()

        Test.objects.create(test=15, callback=self.stop)
        test2 = self.wait()

        Test.objects.filter(test__lte=12).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test._id)

        Test.objects.filter(test__lte=15).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(2)
        expect(loaded_tests[0]._id).to_equal(test._id)
        expect(loaded_tests[1]._id).to_equal(test2._id)

    def test_querying_by_exists(self):
        class Test2(Document):
            __collection__ = "EmbeddedExistsTest"
            test = IntField()

        class Test(Document):
            __collection__ = "EmbeddedExistsTestParent"
            test = ReferenceField(Test2)

        Test.objects.delete(callback=self.stop)
        self.wait()
        Test2.objects.delete(callback=self.stop)
        self.wait()

        Test2.objects.create(test=10, callback=self.stop)
        test2 = self.wait()

        Test.objects.create(test=test2, callback=self.stop)
        test = self.wait()

        Test.objects.create(callback=self.stop)
        self.wait()

        Test.objects.filter(test__exists=True).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(2)
        expect(loaded_tests[0]._id).to_equal(test._id)

    def test_querying_by_is_null(self):
        class Child(Document):
            __collection__ = "EmbeddedIsNullTest"
            num = IntField()

        class Parent(Document):
            __collection__ = "EmbeddedIsNullTestParent"
            child = ReferenceField(Child)

        Parent.objects.delete(callback=self.stop)
        self.wait()
        Child.objects.delete(callback=self.stop)
        self.wait()

        Child.objects.create(num=10, callback=self.stop)
        child = self.wait()

        Parent.objects.create(child=child, callback=self.stop)
        parent = self.wait()

        Parent.objects.create(callback=self.stop)
        parent2 = self.wait()

        Parent.objects.filter(child__is_null=True).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(parent2._id)

        Parent.objects.filter(child__is_null=False).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(parent._id)

    def test_querying_by_multiple_operators(self):
        class Child(Document):
            __collection__ = "MultipleOperatorsTest"
            num = IntField()

        Child.objects.delete(callback=self.stop)
        self.wait()

        Child.objects.create(num=10, callback=self.stop)
        child = self.wait()

        Child.objects.create(num=7, callback=self.stop)
        self.wait()

        Child.objects.create(num=12, callback=self.stop)
        self.wait()

        Child.objects.filter(num__gt=8, num__lt=11).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(child._id)

    def test_querying_by_not(self):
        class Child(Document):
            __collection__ = "NotOperatorTest"
            num = IntField()

        Child.objects.delete(callback=self.stop)
        self.wait()

        Child.objects.create(num=10, callback=self.stop)
        self.wait()

        Child.objects.create(num=7, callback=self.stop)
        child = self.wait()

        Child.objects.filter_not(num__gt=8).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(child._id)

        Child.objects.filter_not(num=10).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(child._id)

    def test_querying_by_in(self):
        dt1 = datetime(2010, 10, 10, 10, 10, 10)
        dt2 = datetime(2011, 10, 10, 10, 10, 10)
        dt3 = datetime(2012, 10, 10, 10, 10, 10)

        class Child(Document):
            __collection__ = "InOperatorTest"
            dt = DateTimeField()

        Child.objects.delete(callback=self.stop)
        self.wait()

        Child.objects.create(dt=dt1, callback=self.stop)
        child = self.wait()

        Child.objects.create(dt=dt2, callback=self.stop)
        child2 = self.wait()

        Child.objects.create(dt=dt3, callback=self.stop)
        child3 = self.wait()

        Child.objects.filter(dt__in=[dt2, dt3]).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(2)
        expect(loaded_parents[0]._id).to_equal(child2._id)
        expect(loaded_parents[1]._id).to_equal(child3._id)

        Child.objects.filter_not(dt__in=[dt2, dt3]).find_all(callback=self.stop)
        loaded_parents = self.wait()

        expect(loaded_parents).to_length(1)
        expect(loaded_parents[0]._id).to_equal(child._id)

    def test_querying_in_an_embedded_document(self):
        class TestEmbedded(Document):
            __collection__ = "TestEmbedded"
            num = IntField()

        class Test(Document):
            __collection__ = "TestEmbeddedParent"
            test = EmbeddedDocumentField(TestEmbedded)

        Test.objects.delete(callback=self.stop)
        self.wait()

        Test.objects.create(test=TestEmbedded(num=10), callback=self.stop)
        test = self.wait()

        Test.objects.create(test=TestEmbedded(num=15), callback=self.stop)
        self.wait()

        Test.objects.filter(test__num__lte=12).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test._id)

        Test.objects.filter(test__num=10).find_all(callback=self.stop)
        loaded_tests = self.wait()

        expect(loaded_tests).to_length(1)
        expect(loaded_tests[0]._id).to_equal(test._id)

    def test_can_update_multiple_documents(self):
        User.objects.create(email="email@gmail.com", first_name="First", last_name="Last2", callback=self.stop)
        self.wait()

        User.objects.create(email="email2@gmail.com", first_name="First2", last_name="Last2", callback=self.stop)
        self.wait()
        User.objects.create(email="email3@gmail.com", first_name="First3", last_name="Last3", callback=self.stop)
        self.wait()
        User.objects.create(email="email4@gmail.com", first_name="First4", last_name="Last4", callback=self.stop)
        self.wait()

        User.objects.filter(first_name__in=["First2", "First3"]).update({
            User.first_name: "Second"
        }, callback=self.stop)
        result = self.wait()

        expect(result.count).to_equal(2)
        expect(result.updated_existing).to_be_true()

        User.objects.filter(first_name="Second").count(callback=self.stop)
        count = self.wait()

        expect(count).to_equal(2)

        User.objects.update({
            User.last_name: "NewLast"
        }, callback=self.stop)
        result = self.wait()

        expect(result.count).to_equal(4)
        expect(result.updated_existing).to_be_true()

        User.objects.filter(last_name="NewLast").count(callback=self.stop)
        count = self.wait()

        expect(count).to_equal(4)

    def test_skip(self):
        User.objects.create(email="email@gmail.com", first_name="First", last_name="Last", callback=self.stop)
        self.wait()
        User.objects.create(email="email2@gmail.com", first_name="First2", last_name="Last2", callback=self.stop)
        self.wait()
        User.objects.create(email="email3@gmail.com", first_name="First3", last_name="Last3", callback=self.stop)
        self.wait()
        User.objects.create(email="email4@gmail.com", first_name="First4", last_name="Last4", callback=self.stop)
        self.wait()

        User.objects.order_by(User.email).skip(2).limit(1).find_all(callback=self.stop)
        users = self.wait()

        expect(users).to_length(1)

    def test_on_save_field(self):
        class SizeDocument(Document):
            items = ListField(IntField())
            item_size = IntField(default=0, on_save=lambda doc, creating: len(doc.items))

        SizeDocument.objects.create(items=[1, 2, 3], callback=self.stop)
        doc = self.wait()

        SizeDocument.objects.get(doc._id, callback=self.stop)
        loaded = self.wait()

        expect(loaded.item_size).to_equal(3)

        loaded.items = [1, 2, 3, 4, 5]
        loaded.save(callback=self.stop)
        self.wait()

        SizeDocument.objects.get(doc._id, callback=self.stop)
        loaded = self.wait()

        expect(loaded.item_size).to_equal(5)

    def test_unique_field(self):
        class UniqueFieldDocument(Document):
            name = StringField(unique=True)

        UniqueFieldDocument.objects.delete(callback=self.stop)
        self.wait()

        UniqueFieldDocument.ensure_index(callback=self.stop)
        self.wait()

        UniqueFieldDocument.objects.create(name="test", callback=self.stop)
        self.wait()

        msg = 'The index "test.UniqueFieldDocument.$name_1" was violated when trying to save this "UniqueFieldDocument" (error code: E11000).'
        with expect.error_to_happen(UniqueKeyViolationError):
            UniqueFieldDocument.objects.create(name="test", callback=self.stop)
            self.wait()

    def test_json_field_with_document(self):
        class JSONFieldDocument(Document):
            field = JsonField()

        obj = [
            {"a": 1},
            {"b": 2}
        ]

        JSONFieldDocument.objects.create(field=obj, callback=self.stop)
        doc = self.wait()

        JSONFieldDocument.objects.get(doc._id, callback=self.stop)
        loaded = self.wait()

        expect(loaded.field).to_be_like([
            {"a": 1},
            {"b": 2}
        ])

    def test_dynamic_fields(self):
        class DynamicFieldDocument(Document):
            __collection__ = "TestDynamicFieldDocument"

        self.drop_coll(DynamicFieldDocument.__collection__)

        obj = {
            "a": 1,
            "b": 2
        }

        DynamicFieldDocument.objects.create(callback=self.stop, **obj)
        doc = self.wait()

        expect(doc._id).not_to_be_null()
        expect(doc.a).to_equal(1)
        expect(doc.b).to_equal(2)

        DynamicFieldDocument.objects.get(doc._id, self.stop)
        loaded_document = self.wait()

        expect(loaded_document.a).to_equal(1)
        expect(loaded_document.b).to_equal(2)

    def test_dynamic_fields_when_saving(self):
        class DynamicFieldDocument(Document):
            __collection__ = "TestDynamicFieldDocumentWhenSaving"

        self.drop_coll(DynamicFieldDocument.__collection__)

        doc = DynamicFieldDocument()
        doc.a = 1
        doc.b = 2
        doc.save(callback=self.stop)
        doc = self.wait()

        expect(doc._id).not_to_be_null()
        expect(doc.a).to_equal(1)
        expect(doc.b).to_equal(2)

        DynamicFieldDocument.objects.get(doc._id, self.stop)
        loaded_document = self.wait()

        expect(loaded_document.a).to_equal(1)
        expect(loaded_document.b).to_equal(2)

    def test_dynamic_fields_multiple_value(self):
        class DynamicFieldDocument(Document):
            __collection__ = "TestDynamicFieldDocumentMultipleValue"

        self.drop_coll(DynamicFieldDocument.__collection__)

        doc = DynamicFieldDocument()
        doc.a = [1, 2, 3, 4]
        doc.save(callback=self.stop)
        doc = self.wait()

        expect(doc._id).not_to_be_null()
        expect(doc.a).to_be_like([1, 2, 3, 4])

        DynamicFieldDocument.objects.get(a=[1, 2, 3, 4], callback=self.stop)
        loaded_document = self.wait()

        expect(loaded_document._id).to_equal(doc._id)

        DynamicFieldDocument.objects.get(a=1, callback=self.stop)
        loaded_document = self.wait()

        expect(loaded_document._id).to_equal(doc._id)

    def test_dynamic_fields_query(self):
        class DynamicFieldDocument(Document):
            __collection__ = "TestDynamicFieldDocumentQuery"

        self.drop_coll(DynamicFieldDocument.__collection__)

        obj = {
            "a": 1,
            "b": 2
        }

        DynamicFieldDocument.objects.create(callback=self.stop, **obj)
        doc = self.wait()

        expect(doc._id).not_to_be_null()
        expect(doc.a).to_equal(1)

        DynamicFieldDocument.objects.filter(**obj).count(callback=self.stop)
        document_count = self.wait()

        expect(document_count).to_equal(1)

    def test_can_query_by_elem_match(self):
        class ElemMatchDocument(Document):
            items = ListField(IntField())

        self.drop_coll(ElemMatchDocument.__collection__)

        ElemMatchDocument.objects.create(items=[1, 2, 3, 4], callback=self.stop)
        doc = self.wait()

        ElemMatchDocument.objects.get(items=1, callback=self.stop)
        loaded_document = self.wait()

        expect(loaded_document._id).to_equal(doc._id)

    def test_can_query_by_elem_match_when_list_of_embedded(self):
        class ElemMatchEmbeddedDocument(Document):
            name = StringField()

        class ElemMatchEmbeddedParentDocument(Document):
            items = ListField(EmbeddedDocumentField(ElemMatchEmbeddedDocument))

        self.drop_coll(ElemMatchEmbeddedDocument.__collection__)
        self.drop_coll(ElemMatchEmbeddedParentDocument.__collection__)

        ElemMatchEmbeddedParentDocument.objects.create(items=[ElemMatchEmbeddedDocument(name="a"), ElemMatchEmbeddedDocument(name="b")], callback=self.stop)
        doc = self.wait()

        ElemMatchEmbeddedParentDocument.objects.create(items=[ElemMatchEmbeddedDocument(name="c"), ElemMatchEmbeddedDocument(name="d")], callback=self.stop)
        doc2 = self.wait()

        ElemMatchEmbeddedParentDocument.objects.filter(items__name="b").find_all(callback=self.stop)
        loaded_document = self.wait()

        expect(loaded_document).to_length(1)

    def test_raw_query(self):
        class RawQueryEmbeddedDocument(Document):
            name = StringField()

        class RawQueryDocument(Document):
            items = ListField(EmbeddedDocumentField(RawQueryEmbeddedDocument))

        self.drop_coll(RawQueryEmbeddedDocument.__collection__)
        self.drop_coll(RawQueryDocument.__collection__)

        RawQueryDocument.objects.create(items=[RawQueryEmbeddedDocument(name='a'), RawQueryEmbeddedDocument(name='b')], callback=self.stop)
        doc = self.wait()

        RawQueryDocument.objects.create(items=[RawQueryEmbeddedDocument(name='c'), RawQueryEmbeddedDocument(name='d')], callback=self.stop)
        doc2 = self.wait()

        RawQueryDocument.objects.filter({"items.name":"a"}).find_all(callback=self.stop)
        items = self.wait()

        expect(items).to_length(1)

    @gen_test
    def test_list_field_with_reference_field(self):
        class Ref(Document):
            __collection__ = 'ref'
            val = StringField()

        class Base(Document):
            __collection__ = 'base'
            list_val = ListField(ReferenceField(reference_document_type=Ref))

        yield Ref.objects.delete()
        yield Base.objects.delete()

        ref1 = yield Ref.objects.create(val="v1")
        ref2 = yield Ref.objects.create(val="v2")
        ref3 = yield Ref.objects.create(val="v3")

        base = yield Base.objects.create(list_val=[ref1, ref2, ref3])

        base = yield Base.objects.get(base._id)
        expect(base).not_to_be_null()

        yield base.load_references()
        expect(base.list_val).to_length(3)
        expect(base.list_val[0]).to_be_instance_of(Ref)

    @gen_test
    def test_list_field_with_reference_field_without_lazy(self):
        class Ref(Document):
            __collection__ = 'ref'
            val = StringField()

        class Base(Document):
            __collection__ = 'base'
            __lazy__ = False
            list_val = ListField(ReferenceField(reference_document_type=Ref))

        yield Ref.objects.delete()
        yield Base.objects.delete()

        ref1 = yield Ref.objects.create(val="v1")
        ref2 = yield Ref.objects.create(val="v2")
        ref3 = yield Ref.objects.create(val="v3")

        base = yield Base.objects.create(list_val=[ref1, ref2, ref3])

        base = yield Base.objects.get(base._id)
        expect(base).not_to_be_null()

        expect(base.list_val).to_length(3)
        expect(base.list_val[0]).to_be_instance_of(Ref)
