#!/usr/bin/env python

# -*- coding: utf-8 -*-

from uuid import uuid4

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestUUIDField'}
    uuid = mongoengine.UUIDField()


class MotorDocument(motorengine.Document):
    __collection__ = "IntegrationTestUUIDField"
    uuid = motorengine.UUIDField()


class TestUUIDField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(uuid=uuid4()).save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.uuid).to_equal(mongo_document.uuid)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(uuid=uuid4())

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.uuid).to_equal(motor_document.uuid)
