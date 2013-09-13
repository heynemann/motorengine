#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import motorengine
import mongoengine

from tests.integration.base import BaseIntegrationTest


class TestBooleanField(BaseIntegrationTest):
    def test_can_integrate(self):
        class MongoDocument(mongoengine.Document):
            meta = {'collection': 'IntegrationTestBooleanField'}
            is_active = mongoengine.BooleanField()

        class MotorDocument(motorengine.Document):
            __collection__ = "IntegrationTestBooleanField"
            is_active = motorengine.BooleanField()

        mongo_document = MongoDocument(is_active=True).save()

        MotorDocument.objects.get(mongo_document.id, self.stop)

        result = self.wait()['kwargs']['instance']
        expect(result._id).to_equal(mongo_document.id)
        expect(result.is_active).to_be_true()
