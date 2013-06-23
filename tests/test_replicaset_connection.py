import sys
sys.path[0:0] = [""]
import unittest

import pymongo
from pymongo import ReadPreference, ReplicaSetConnection

import motorengine
from motorengine import *
from motorengine.connection import get_db, get_connection, ConnectionError


class ConnectionTest(unittest.TestCase):

    def tearDown(self):
        motorengine.connection._connection_settings = {}
        motorengine.connection._connections = {}
        motorengine.connection._dbs = {}

    def test_replicaset_uri_passes_read_preference(self):
        """Requires a replica set called "rs" on port 27017
        """

        try:
            conn = connect(db='motorenginetest', host="mongodb://localhost/mongoenginetest?replicaSet=rs", read_preference=ReadPreference.SECONDARY_ONLY)
        except ConnectionError, e:
            return

        if not isinstance(conn, ReplicaSetConnection):
            return

        self.assertEqual(conn.read_preference, ReadPreference.SECONDARY_ONLY)

if __name__ == '__main__':
    unittest.main()
