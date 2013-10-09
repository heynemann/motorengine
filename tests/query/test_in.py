#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4

from preggy import expect

from motorengine.fields.uuid_field import UUIDField
from motorengine.query.in_operator import InQueryOperator
from tests import AsyncTestCase


class TestInQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = InQueryOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", [10, 20])).to_be_like({
            "field_name": {
                "$in": [10, 20]
            }
        })

    def test_get_value(self):
        field = UUIDField()
        query = InQueryOperator()

        uuid1 = uuid4()
        uuid2 = uuid4()

        expect(query.get_value(field, [str(uuid1), str(uuid2)])).to_be_like([uuid1, uuid2])
