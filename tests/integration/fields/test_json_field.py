#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test
from ujson import dumps, loads

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestJsonField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    data = mongoengine.StringField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    data = motorengine.JsonField()

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
