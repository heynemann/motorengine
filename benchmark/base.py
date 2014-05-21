#!/usr/bin/env python
# -*- coding: utf-8 -*-

import motorengine
import mongoengine
import motor
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase


class BenchmarkTest(AsyncHTTPTestCase, LogTrapTestCase):
    def setUp(self):
        super(BenchmarkTest, self).setUp()

        self.db = motorengine.connect("test", host="localhost", port=27017, io_loop=self.io_loop)
        mongoengine.connect("test", host="localhost", port=27017)
        self.motor = motor.MotorClient('localhost', 27017, io_loop=self.io_loop, max_concurrent=500).open_sync()

    def tearDown(self):
        motorengine.connection.cleanup()
        super(AsyncHTTPTestCase, self).tearDown()
