#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import motorengine
import mongoengine


from tests.integration.base import BaseIntegrationTest


class TestDocument(BaseIntegrationTest):
    def test_can_save_document(self):
        class MongoUser(mongoengine.Document):
            meta = {'collection': 'IntegrationTestUsers'}
            email = mongoengine.StringField()

        class MotorUser(motorengine.Document):
            __collection__ = "IntegrationTestUsers"
            email = motorengine.StringField()

        mongo_user = MongoUser(email="test@test.com").save()

        MotorUser.objects.get(mongo_user.id, self.stop)

        result = self.wait()['kwargs']['instance']
        expect(result._id).to_equal(mongo_user.id)
        expect(result.email).to_equal("test@test.com")
