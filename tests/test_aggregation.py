#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time

from preggy import expect

from motorengine import (
    Document, StringField, BooleanField, ListField,
    DESCENDING, DateTimeField, IntField, Aggregation
)
from tests import AsyncTestCase


class User(Document):
    __collection__ = "AggregationUser"

    email = StringField(required=True)
    first_name = StringField(max_length=50, default=lambda: "Bernardo")
    last_name = StringField(max_length=50, default="Heynemann")
    is_admin = BooleanField(default=True)
    updated_at = DateTimeField(required=True, auto_now_on_insert=True, auto_now_on_update=True)
    number_of_documents = IntField()
    list_items = ListField(IntField())


class TestAggregation(AsyncTestCase):
    def setUp(self):
        super(TestAggregation, self).setUp()
        self.drop_coll("AggregationUser")
        self.add_users()

    def add_users(self):
        users = []
        for i in range(100):
            users.append(User(
                email="heynemann@gmail.com",
                first_name="Bernardo%d" % i,
                last_name="Heynemann%d" % i,
                is_admin=i % 2 == 0,
                number_of_documents=i * 100,
                list_items=list(range(i)),
            ))

        User.objects.bulk_insert(users, callback=self.stop)
        self.wait()

    def test_can_aggregate_number_of_documents(self):
        print "STARTED AGGREGATION"
        start_time = time()

        User.objects.aggregate(
            group_by=[
                User.email,
                Aggregation.avg(User.number_of_documents, alias="number_of_documents")
            ],
            callback=self.stop
        )

        result = self.wait()

        expect(result).not_to_be_null()
        expect(result).to_length(1)
        expect(result[0].email).to_equal('heynemann@gmail.com')
        expect(result[0].number_of_documents).to_be_like(4950.0)

        print "%.6fs" % (time() - start_time)
