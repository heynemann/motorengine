#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestStringField'}
    name = mongoengine.StringField()


class MotorDocument(motorengine.Document):
    __collection__ = "IntegrationTestStringField"
    name = motorengine.StringField()


class TestStringField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(name="some_string").save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.name).to_equal(mongo_document.name)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(name="other_string")

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.name).to_equal(motor_document.name)
