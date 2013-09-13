#!/usr/bin/env python
# -*- coding: utf-8 -*-


import motorengine
import mongoengine

from tests import AsyncTestCase


class BaseIntegrationTest(AsyncTestCase):
    def setUp(self, auto_connect=True):
        super(AsyncTestCase, self).setUp()
        if auto_connect:
            self.db = motorengine.connect("test", host="localhost", port=4445, io_loop=self.io_loop)
            mongoengine.connect("test", host="localhost", port=4445)

    def tearDown(self):
        motorengine.connection.cleanup()
        super(AsyncTestCase, self).tearDown()
