#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time

import motorengine
import mongoengine
from tornado import gen
import tornado.web
from preggy import expect
from tornado.testing import gen_test

from benchmark.base import BenchmarkTest


class MotorDocument(motorengine.Document):
    field1 = motorengine.StringField()
    field2 = motorengine.IntField()
    field3 = motorengine.DateTimeField(default=datetime.now)


class MongoDocument(mongoengine.Document):
    field1 = mongoengine.StringField()
    field2 = mongoengine.IntField()
    field3 = mongoengine.DateTimeField(default=datetime.now)


class MotorEngineInsertHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = yield MotorDocument.objects.create(
            field1="whatever",
            field2=10
        )
        self.write(str(result._id))
        self.finish()


class MongoEngineInsertHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = MongoDocument.objects.create(
            field1="whatever",
            field2=10
        )
        self.write(str(result.id))
        self.finish()


class TestInsert(BenchmarkTest):
    def get_app(self):
        return tornado.web.Application([
            ('/motor', MotorEngineInsertHandler),
            ('/mongo', MongoEngineInsertHandler)
        ])

    @gen_test
    def test_insert(self):
        iterations = 500

        start = time.time()

        for i in range(iterations):
            yield MotorDocument.objects.create(
                field1="whatever",
                field2=10
            )

        motorengine_db_time = time.time() - start

        start = time.time()

        for i in range(iterations):
            response = self.fetch('/motor')
            expect(response.code).to_equal(200)

        motorengine_time = time.time() - start

        start = time.time()

        for i in range(iterations):
            response = self.fetch('/mongo')
            expect(response.code).to_equal(200)

        mongoengine_time = time.time() - start

        start = time.time()

        for i in range(iterations):
            MongoDocument.objects.create(
                field1="whatever",
                field2=10
            )

        mongoengine_db_time = time.time() - start

        print
        print
        print("[MotorEngine] %d inserts (via DB) done in %.2fs (%.2f ops/s)" % (iterations, motorengine_db_time, (float(iterations) / motorengine_db_time)))
        print("[MotorEngine] %d inserts (via HTTP) done in %.2fs (%.2f ops/s)" % (iterations, motorengine_time, (float(iterations) / motorengine_time)))
        print("[MongoEngine] %d inserts (via DB) done in %.2fs (%.2f ops/s)" % (iterations, mongoengine_db_time, (float(iterations) / mongoengine_db_time)))
        print("[MongoEngine] %d inserts (via HTTP) done in %.2fs (%.2f ops/s)" % (iterations, mongoengine_time, (float(iterations) / mongoengine_time)))
        print
        print

        #expect(motorengine_time).to_be_lesser_than(mongoengine_time)
