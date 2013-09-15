#!/usr/bin/env python

# -*- coding: utf-8 -*-

from datetime import datetime

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestDateTimeField'}
    date = mongoengine.DateTimeField()


class MotorDocument(motorengine.Document):
    __collection__ = "IntegrationTestDateTimeField"
    date = motorengine.DateTimeField()


class TestDatetimeField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(date=datetime.now()).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.date).to_be_like(mongo_document.date)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(date=datetime.now())

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.date).to_be_like(motor_document.date)
