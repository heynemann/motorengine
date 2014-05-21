#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import motorengine
import mongoengine
from tornado import gen
import tornado.web


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


def get_app():
    return tornado.web.Application([
        ('/motor/insert', MotorEngineInsertHandler),
        ('/mongo/insert', MongoEngineInsertHandler)
    ])


if __name__ == "__main__":
    application = get_app()
    application.listen(8888)
    io_loop = tornado.ioloop.IOLoop.instance()

    motorengine.connect("test", host="localhost", port=27017, io_loop=io_loop)
    mongoengine.connect("test", host="localhost", port=27017)

    io_loop.start()
