#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestURLField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    url = mongoengine.URLField()


class MotorDocument(motorengine.Document):
    __collection__ = COLLECTION
    url = motorengine.URLField()


class TestURLField(BaseIntegrationTest):
    @gen_test
    def test_can_integrate(self):
        mongo_document = MongoDocument(url="http://www.google.com/").save()

        result = yield MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.url).to_equal(mongo_document.url)

    @gen_test
    def test_can_integrate_backwards(self):
        motor_document = yield MotorDocument.objects.create(url="http://www.wikipedia.org/")

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.url).to_equal(motor_document.url)
