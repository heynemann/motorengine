#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect

from motorengine import connect
from motorengine.connection import ConnectionError
from tests import AsyncTestCase


class TestConnect(AsyncTestCase):
    def setUp(self):
        super(TestConnect, self).setUp(auto_connect=False)

    def test_can_connect_to_a_database(self):
        db = connect('test', host="localhost", port=4445, io_loop=self.io_loop)

        args, kwargs = self.exec_async(db.ping)
        ping_result = args[0]['ok']
        expect(ping_result).to_equal(1.0)

    def test_connect_to_replica_set(self):
        db = connect('test', host="localhost:27017,localhost:27018", replicaSet="rs0", port=4445, io_loop=self.io_loop)

        args, kwargs = self.exec_async(db.ping)
        ping_result = args[0]['ok']
        expect(ping_result).to_equal(1.0)

    def test_connect_to_replica_set_with_invalid_replicaset_name(self):
        try:
            connect('test', host="localhost:27017,localhost:27018", replicaSet=0, port=4445, io_loop=self.io_loop)
        except ConnectionError:
            exc_info = sys.exc_info()[1]
            expect(str(exc_info)).to_include('the replicaSet keyword parameter is required')
        else:
            assert False, "Should not have gotten this far"
