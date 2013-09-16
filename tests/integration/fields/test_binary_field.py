#!/usr/bin/env python

# -*- coding: utf-8 -*-

import six
from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = "IntegrationTestBinaryField"


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    byte = mongoengine.BinaryField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    byte = motorengine.BinaryField()


class TestStringField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(byte=six.b("some_string")).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.byte).to_equal(mongo_document.byte)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(byte=six.b("other_string"))

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.byte).to_equal(motor_document.byte)
