#!/usr/bin/env python

# -*- coding: utf-8 -*-

from preggy import expect
import mongoengine
from tornado.testing import gen_test

import motorengine


from tests.integration.base import BaseIntegrationTest


class TestDocument(BaseIntegrationTest):
    @gen_test
    def test_can_save_document(self):
        class MongoUser(mongoengine.Document):
            meta = {'collection': 'IntegrationTestUsers'}
            email = mongoengine.StringField()

        class MotorUser(motorengine.Document):
            __collection__ = "IntegrationTestUsers"
            email = motorengine.StringField()

        mongo_user = MongoUser(email="test@test.com").save()

        result = yield MotorUser.objects.get(mongo_user.id)

        expect(result._id).to_equal(mongo_user.id)
        expect(result.email).to_equal("test@test.com")

    @gen_test
    def test_can_save_embedded_document(self):
        class MongoBase(mongoengine.EmbeddedDocument):
            meta = {'collection': 'IntegrationTestEmbeddedBase'}
            string = mongoengine.StringField()

        class MongoDoc(mongoengine.Document):
            meta = {'collection': 'IntegrationTestEmbeddedDoc'}
            embed = mongoengine.EmbeddedDocumentField(MongoBase)

        class MotorBase(motorengine.Document):
            __collection__ = 'IntegrationTestEmbeddedBase'
            string = motorengine.StringField()

        class MotorDoc(motorengine.Document):
            __collection__ = 'IntegrationTestEmbeddedDoc'
            embed = motorengine.EmbeddedDocumentField(MotorBase)

        mongo_doc = MongoDoc(embed=MongoBase(string="test@test.com")).save()

        result = yield MotorDoc.objects.get(mongo_doc.id)

        expect(result).not_to_be_null()

        expect(result._id).to_equal(mongo_doc.id)
        expect(result.embed.string).to_equal("test@test.com")

    @gen_test
    def test_can_save_reference_field(self):
        class MongoBase(mongoengine.Document):
            meta = {'collection': 'IntegrationTestRefBase'}
            string = mongoengine.StringField()

        class MongoDoc(mongoengine.Document):
            meta = {'collection': 'IntegrationTestRefDoc'}
            embed = mongoengine.ReferenceField(MongoBase)

        class MotorBase(motorengine.Document):
            __collection__ = 'IntegrationTestRefBase'
            string = motorengine.StringField()

        class MotorDoc(motorengine.Document):
            __collection__ = 'IntegrationTestRefDoc'
            embed = motorengine.ReferenceField(MotorBase)

        mongo_base = MongoBase(string="test@test.com").save()
        mongo_doc = MongoDoc(embed=mongo_base).save()

        result = yield MotorDoc.objects.get(mongo_doc.id)

        yield result.load_references()

        expect(result).not_to_be_null()

        expect(result._id).to_equal(mongo_doc.id)
        expect(result.embed.string).to_equal("test@test.com")

    @gen_test
    def test_can_delete_items(self):
        class MotorDoc(motorengine.Document):
            __collection__ = 'IntegrationCanDeleteOneItem'
            string = motorengine.StringField()

        yield MotorDoc.objects.delete()

        item = yield MotorDoc.objects.create(string="test1")
        item2 = yield MotorDoc.objects.create(string="test2")
        item3 = yield MotorDoc.objects.create(string="test3")
        item4 = yield MotorDoc.objects.create(string="test4")

        all_items = yield MotorDoc.objects.find_all()

        expect(all_items).to_length(4)

        deleted = yield item.delete()
        expect(deleted).to_equal(1)

        all_items = yield MotorDoc.objects.find_all()

        expect(all_items).to_length(3)
        expect(all_items[0]._id).to_equal(item2._id)
        expect(all_items[1]._id).to_equal(item3._id)
        expect(all_items[2]._id).to_equal(item4._id)

        deleted = yield MotorDoc.objects.filter(string="test4").delete()
        expect(deleted).to_equal(1)

        all_items = yield MotorDoc.objects.find_all()

        expect(all_items).to_length(2)
        expect(all_items[0]._id).to_equal(item2._id)
        expect(all_items[1]._id).to_equal(item3._id)

        deleted = yield MotorDoc.objects.delete()
        expect(deleted).to_equal(2)

        cnt = yield MotorDoc.objects.count()

        expect(cnt).to_equal(0)
