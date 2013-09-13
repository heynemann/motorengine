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

        MotorDoc.objects.get(mongo_doc.id, self.stop)

        result = self.wait()['kwargs']['instance']

        expect(result).not_to_be_null()

        expect(result._id).to_equal(mongo_doc.id)
        expect(result.embed.string).to_equal("test@test.com")

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

        MotorDoc.objects.get(mongo_doc.id, self.stop)

        result = self.wait()['kwargs']['instance']

        result.load_references(self.stop)
        self.wait()

        expect(result).not_to_be_null()

        expect(result._id).to_equal(mongo_doc.id)
        expect(result.embed.string).to_equal("test@test.com")
