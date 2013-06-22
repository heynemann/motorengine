#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
import motor

from motorengine import connect, disconnect
from tests import AsyncTestCase


class TestDatabase(AsyncTestCase):
    def test_database_ping(self):
        db = connect("test", host="localhost", port=4445, io_loop=self.io_loop)

        args, kwargs = self.exec_async(db.ping)
        ping_result = args[0]['ok']
        expect(ping_result).to_equal(1.0)

        disconnect()

    def test_database_returns_collection_when_asked_for_a_name(self):
        db = connect("test", host="localhost", port=4445, io_loop=self.io_loop)

        expect(db.something).to_be_instance_of(motor.MotorCollection)
