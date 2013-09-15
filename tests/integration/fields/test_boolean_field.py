#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestBooleanField'}
    is_active = mongoengine.BooleanField()


class MotorDocument(motorengine.Document):
    __collection__ = "IntegrationTestBooleanField"
    is_active = motorengine.BooleanField()


class TestBooleanField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(is_active=True).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.is_active).to_be_true()

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(is_active=True)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.is_active).to_be_true()
