#!/usr/bin/env python

# -*- coding: utf-8 -*-

from datetime import datetime

from preggy import expect
import motorengine
import mongoengine

from tests.integration.base import BaseIntegrationTest


class TestDatetimeField(BaseIntegrationTest):
    def test_can_integrate(self):
        class MongoDocument(mongoengine.Document):
            meta = {'collection': 'IntegrationTestDateTimeField'}
            date = mongoengine.DateTimeField()

        class MotorDocument(motorengine.Document):
            __collection__ = "IntegrationTestDateTimeField"
            date = motorengine.DateTimeField()

        mongo_document = MongoDocument(date=datetime.now()).save()

        MotorDocument.objects.get(mongo_document.id, self.stop)

        result = self.wait()['kwargs']['instance']
        expect(result._id).to_equal(mongo_document.id)
        expect(result.date).to_be_like(mongo_document.date)
