# -*- coding: utf-8 -*-
import unittest

from motorengine import Document, connect
from motorengine.connection import get_db
from motorengine.fields import StringField

__all__ = ('ConvertToNewInheritanceModel', )


class ConvertToNewInheritanceModel(unittest.TestCase):

    def setUp(self):
        connect(db='motorenginetest')
        self.db = get_db()

    def tearDown(self):
        for collection in self.db.collection_names():
            if 'system.' in collection:
                continue
            self.db.drop_collection(collection)

    def test_how_to_convert_to_the_new_inheritance_model(self):
        """Demonstrates migrating from 0.7 to 0.8
        """

        # 1. Declaration of the class
        class Animal(Document):
            name = StringField()
            meta = {
                'allow_inheritance': True,
                'indexes': ['name']
            }

        # 2. Remove _types
        collection = Animal._get_collection()
        collection.update({}, {"$unset": {"_types": 1}}, multi=True)

        # 3. Confirm extra data is removed
        count = collection.find({'_types': {"$exists": True}}).count()
        self.assertEqual(0, count)

        # 4. Remove indexes
        info = collection.index_information()
        indexes_to_drop = [key for key, value in info.iteritems()
                           if '_types' in dict(value['key'])]
        for index in indexes_to_drop:
            collection.drop_index(index)

        # 5. Recreate indexes
        Animal.ensure_indexes()
