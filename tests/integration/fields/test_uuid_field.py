#!/usr/bin/env python

# -*- coding: utf-8 -*-

from uuid import uuid4

from preggy import expect
import motorengine
import mongoengine

from tests.integration.base import BaseIntegrationTest


class TestUUIDField(BaseIntegrationTest):
    def test_can_integrate(self):
        class MongoDocument(mongoengine.Document):
            meta = {'collection': 'IntegrationTestUUIDField'}
            uuid = mongoengine.UUIDField()

        class MotorDocument(motorengine.Document):
            __collection__ = "IntegrationTestUUIDField"
            uuid = motorengine.UUIDField()

        mongo_document = MongoDocument(uuid=uuid4()).save()

        MotorDocument.objects.get(mongo_document.id, self.stop)

        result = self.wait()['kwargs']['instance']
        expect(result._id).to_equal(mongo_document.id)
        expect(result.uuid).to_equal(mongo_document.uuid)
