import sys
sys.path[0:0] = [""]
import unittest
import datetime

import pymongo
from bson.tz_util import utc

from motorengine import *
import motorengine.connection
from motorengine.connection import get_db, get_connection, ConnectionError


class ConnectionTest(unittest.TestCase):

    def tearDown(self):
        motorengine.connection._connection_settings = {}
        motorengine.connection._connections = {}
        motorengine.connection._dbs = {}

    def test_connect(self):
        """Ensure that the connect() method works properly.
        """
        connect('motorenginetest')

        conn = get_connection()
        self.assertTrue(isinstance(conn, pymongo.mongo_client.MongoClient))

        db = get_db()
        self.assertTrue(isinstance(db, pymongo.database.Database))
        self.assertEqual(db.name, 'motorenginetest')

        connect('motorenginetest2', alias='testdb')
        conn = get_connection('testdb')
        self.assertTrue(isinstance(conn, pymongo.mongo_client.MongoClient))

    def test_connect_uri(self):
        """Ensure that the connect() method works properly with uri's
        """
        c = connect(db='motorenginetest', alias='admin')
        c.admin.system.users.remove({})
        c.motorenginetest.system.users.remove({})

        c.admin.add_user("admin", "password")
        c.admin.authenticate("admin", "password")
        c.motorenginetest.add_user("username", "password")

        self.assertRaises(ConnectionError, connect, "testdb_uri_bad", host='mongodb://test:password@localhost')

        connect("testdb_uri", host='mongodb://username:password@localhost/motorenginetest')

        conn = get_connection()
        self.assertTrue(isinstance(conn, pymongo.mongo_client.MongoClient))

        db = get_db()
        self.assertTrue(isinstance(db, pymongo.database.Database))
        self.assertEqual(db.name, 'motorenginetest')

    def test_register_connection(self):
        """Ensure that connections with different aliases may be registered.
        """
        register_connection('testdb', 'motorenginetest2')

        self.assertRaises(ConnectionError, get_connection)
        conn = get_connection('testdb')
        self.assertTrue(isinstance(conn, pymongo.mongo_client.MongoClient))

        db = get_db('testdb')
        self.assertTrue(isinstance(db, pymongo.database.Database))
        self.assertEqual(db.name, 'motorenginetest2')

    def test_connection_kwargs(self):
        """Ensure that connection kwargs get passed to pymongo.
        """
        connect('motorenginetest', alias='t1', tz_aware=True)
        conn = get_connection('t1')

        self.assertTrue(conn.tz_aware)

        connect('motorenginetest2', alias='t2')
        conn = get_connection('t2')
        self.assertFalse(conn.tz_aware)

    def test_datetime(self):
        connect('motorenginetest', tz_aware=True)
        d = datetime.datetime(2010, 5, 5, tzinfo=utc)

        class DateDoc(Document):
            the_date = DateTimeField(required=True)

        DateDoc.drop_collection()
        DateDoc(the_date=d).save()

        date_doc = DateDoc.objects.first()
        self.assertEqual(d, date_doc.the_date)


if __name__ == '__main__':
    unittest.main()
