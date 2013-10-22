#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from tornado.testing import gen_test

from motorengine import (
    Document, StringField, BooleanField,
    URLField, DateTimeField, Q, EmbeddedDocumentField
)
from motorengine.query_builder.node import QCombination
from tests import AsyncTestCase


class EmbeddedDocument(Document):
    test = StringField(db_field="other", required=True)


class User(Document):
    email = StringField(required=True)
    first_name = StringField(db_field="whatever", max_length=50, default=lambda: "Bernardo")
    last_name = StringField(max_length=50, default="Heynemann")
    is_admin = BooleanField(default=True)
    website = URLField(default="http://google.com/")
    updated_at = DateTimeField(required=True, auto_now_on_insert=True, auto_now_on_update=True)
    embedded = EmbeddedDocumentField(EmbeddedDocument, db_field="embedded_document")

    def __repr__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class TestQueryBuilder(AsyncTestCase):
    def setUp(self):
        super(TestQueryBuilder, self).setUp()
        self.drop_coll("User")

    def test_gets_proper_type(self):
        query = Q(first_name="Test")
        expect(query).to_be_instance_of(Q)

        query = Q(first_name="Test") | Q(first_name="Else")
        expect(query).to_be_instance_of(QCombination)

    def test_gets_proper_query(self):
        query = Q(first_name="Test")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            "whatever": "Test"
        })

    def test_gets_proper_query_when_query_operator_used(self):
        query = Q(first_name__lte="Test")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            "whatever": {"$lte": "Test"}
        })

    def test_gets_proper_query_when_embedded_document(self):
        query = Q(embedded__test__lte="Test")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            "embedded_document.other": {"$lte": "Test"}
        })

    def test_gets_proper_query_when_and(self):
        query = Q(embedded__test__lte="Test") & Q(first_name="Someone")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            "embedded_document.other": {"$lte": "Test"},
            "whatever": "Someone"
        })

    def test_gets_proper_query_when_or(self):
        query = Q(first_name="Someone") | Q(first_name="Else")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            '$or': [
                {'whatever': 'Someone'},
                {'whatever': 'Else'}
            ]
        })

    def test_gets_proper_query_when_many_operators(self):
        query = (Q(embedded__test__lte="Test") & Q(first_name="Someone")) | Q(first_name="Else")
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            '$or': [
                {
                    'embedded_document.other': {'$lte': 'Test'},
                    'whatever': 'Someone'
                },
                {'whatever': 'Else'}
            ]
        })

    def test_gets_proper_query_when_many_operators_with_and_first(self):
        query = Q(last_name="Whatever") & ((Q(embedded__test__lte="Test") & Q(first_name="Someone")) | Q(first_name="Else"))
        query_result = query.to_query(User)

        expect(query_result).to_be_like({
            '$and': [
                {'last_name': 'Whatever'},
                {'$or': [
                    {
                        'embedded_document.other': {'$lte': 'Test'},
                        'whatever': 'Someone'
                    },
                    {'whatever': 'Else'}
                ]}
            ]
        })

    def create_test_users(self):
        User.objects.create(
            email="heynemann@gmail.com", first_name="Bernardo", last_name="Heynemann",
            embedded=EmbeddedDocument(test="test"),
            callback=self.stop
        )
        self.user = self.wait()

        User.objects.create(
            email="heynemann@gmail.com", first_name="Someone", last_name="Else",
            embedded=EmbeddedDocument(test="test2"),
            callback=self.stop
        )
        self.user2 = self.wait()

        User.objects.create(
            email="heynemann@gmail.com", first_name="John", last_name="Doe",
            embedded=EmbeddedDocument(test="test3"),
            callback=self.stop
        )
        self.user3 = self.wait()

    #@gen_test
    def test_can_query_using_q(self):
        self.create_test_users()

        User.objects.find_all(callback=self.stop)
        users = self.wait()
        expect(users).to_length(3)

        User.objects.filter(Q(first_name="Bernardo")).find_all(callback=self.stop)
        users = self.wait()
        expect(users).to_length(1)

        User.objects.filter(Q(first_name="Bernardo") | Q(first_name="Someone")).find_all(callback=self.stop)
        users = self.wait()
        expect(users).to_length(2)
