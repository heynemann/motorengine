#!/usr/bin/env python
# -*- coding: utf-8 -*-

import motorengine
import mongoengine
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase


class BenchmarkTest(AsyncHTTPTestCase, LogTrapTestCase):
    def setUp(self):
        super(BenchmarkTest, self).setUp()

        self.db = motorengine.connect("test", host="localhost", port=4445, io_loop=self.io_loop)
        mongoengine.connect("test", host="localhost", port=4445)

    def tearDown(self):
        motorengine.connection.cleanup()
        super(AsyncHTTPTestCase, self).tearDown()
