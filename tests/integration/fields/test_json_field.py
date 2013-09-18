#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

try:
    from ujson import dumps, loads
except:
    from json import dumps, loads

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestJsonField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    data = mongoengine.StringField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    data = motorengine.JsonField()


class Other(motorengine.Document):
    __collection__ = "Other_%s" % COLLECTION
    items = motorengine.ListField(motorengine.EmbeddedDocumentField(MotorDocument))


data = {
    "value": 10,
    "list": [1, 2, "a"],
    "dict": {
        "a": 1,
        "b": 2
    }
}


class TestStringField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(data=dumps(data)).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.data).to_be_like(data)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(data=data)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(loads(result.data)).to_be_like(data)

    @gen_test
    def test_gets_right_types(self):
        motor_document = yield MotorDocument.objects.create(data=10)
        expect(motor_document.data).to_equal(10)

        loaded = yield MotorDocument.objects.get(motor_document._id)
        expect(loaded.data).to_equal(10)

        other = yield Other.objects.create()
        other.items.append(MotorDocument(data=10))
        yield other.save()

        loaded = yield Other.objects.get(other._id)
        expect(other.items).to_length(1)
        expect(other.items[0].data).to_equal(10)
