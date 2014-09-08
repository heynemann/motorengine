#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestFloatField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    number = mongoengine.FloatField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    number = motorengine.FloatField()


class TestFloatField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(number=10.5).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.number).to_equal(mongo_document.number)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(number=10.5)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.number).to_equal(motor_document.number)

    @gen_test
    def test_empty_field(self):
        motor_document = yield MotorDocument.objects.create()

        result = yield MotorDocument.objects.get(id=motor_document._id)

        expect(result).not_to_be_null()
        expect(result.number).to_be_null()
