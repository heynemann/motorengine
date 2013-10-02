#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.base import QueryOperator
from tests import AsyncTestCase


class TestBaseQueryOperator(AsyncTestCase):
    def test_can_create_query_operator(self):
        query = QueryOperator("some value")
        expect(query).not_to_be_null()
        expect(query.value).to_equal("some value")
