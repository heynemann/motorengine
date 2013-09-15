#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestEmailField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    email = mongoengine.EmailField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    email = motorengine.EmailField()


class TestEmailField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(email="someone@gmail.com").save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.email).to_equal(mongo_document.email)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(email="someone@gmail.com")

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.email).to_equal(motor_document.email)
