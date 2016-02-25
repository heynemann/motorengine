#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
# from tornado.testing import gen_test

from motorengine import (
    Document, StringField, EmbeddedDocumentField, ListField, IntField
)

from motorengine.query_builder.field_list import QueryFieldList
from tests import AsyncTestCase


class Name(Document):
    last = StringField(db_field='last_name')
    first = StringField()


class User(Document):
    name = EmbeddedDocumentField(embedded_document_type=Name)
    email = StringField(db_field='email_address')
    numbers = ListField(base_field=IntField())


class TestQueryFieldList(AsyncTestCase):
    def setUp(self):
        super(TestQueryFieldList, self).setUp()

    def test_gets_proper_type(self):
        query1 = QueryFieldList()
        query2 = QueryFieldList()

        expect(query1).to_be_instance_of(QueryFieldList)

        query = query1 + query2

        expect(query).to_be_instance_of(QueryFieldList)

    def test_default_query_field_list(self):
        query = QueryFieldList()

        expect(query).not_to_be_null()
        expect(query.value).to_equal(QueryFieldList.ONLY)
        expect(query.__nonzero__()).not_to_be_true()
        expect(query.__bool__()).not_to_be_true()
        expect(bool(query)).not_to_be_true()

    def test_only_query_field_list(self):
        query = QueryFieldList(['name', 'email'], value=QueryFieldList.ONLY)

        expect(bool(query)).to_be_true()
        expect(query.as_dict()).to_be_like({
            'name': 1, 'email': 1
        })
        expect(query.to_query(User)).to_be_like({
            'name': 1, 'email_address': 1
        })

        query.reset()
        expect(query.as_dict()).to_be_like({})

    def test_exclude_query_field_list(self):
        query = QueryFieldList(
            fields=['name.last', 'email'],
            value=QueryFieldList.EXCLUDE
        )

        expect(bool(query)).to_be_true()
        expect(query.as_dict()).to_be_like({
            'name.last': 0, 'email': 0
        })
        expect(query.to_query(User)).to_be_like({
            'name.last_name': 0, 'email_address': 0
        })

        query.reset()
        expect(query.as_dict()).to_be_like({})

    def test_union_of_queries_when_only_or_exclude_called(self):
        query1 = QueryFieldList(
            fields=['name.last', 'email'],
            value=QueryFieldList.ONLY,
            _only_called=True
        )
        query2 = QueryFieldList(
            fields=['name.first'],
            value=QueryFieldList.ONLY,
            _only_called=True
        )
        query3 = QueryFieldList(
            fields=['email'],
            value=QueryFieldList.EXCLUDE
        )
        query = query1 + query2

        expect(query.as_dict()).to_be_like({
            'name.last': 1, 'email': 1, 'name.first': 1
        })

        query = query + query3

        expect(query.as_dict()).to_be_like({
            'name.last': 1, 'name.first': 1
        })

        # try again exclude 'email' that is not in the fields now
        query = query + QueryFieldList(['email'], value=QueryFieldList.EXCLUDE)

        expect(query.as_dict()).to_be_like({
            'name.last': 1, 'name.first': 1
        })

        # the same but exclude first now
        query = QueryFieldList(['email'], value=QueryFieldList.EXCLUDE) + query

        expect(query.as_dict()).to_be_like({
            'name.last': 1, 'name.first': 1
        })

        # exclude first field present in fields
        query = (
            QueryFieldList(['name.last'], value=QueryFieldList.EXCLUDE) + query
        )

        expect(query.as_dict()).to_be_like({
            'name.first': 1
        })

        # exclude works only with full names not with prefixes
        query = (
            QueryFieldList(['name'], value=QueryFieldList.EXCLUDE) + query
        )

        expect(query.as_dict()).to_be_like({
            'name.first': 1
        })

    def test_union_of_excludes(self):
        query = (
            QueryFieldList(['name'], value=QueryFieldList.EXCLUDE) +
            QueryFieldList(['email', 'numbers'], value=QueryFieldList.EXCLUDE)
        )

        expect(query.as_dict()).to_be_like({
            'name': 0, 'email': 0, 'numbers': 0
        })

    def test_always_include(self):
        query = QueryFieldList(always_include=['email'])
        query += QueryFieldList(
            ['name'], value=QueryFieldList.ONLY, _only_called=True
        )

        expect(query.as_dict()).to_be_like({'name': 1, 'email': 1})

        query = QueryFieldList(
            always_include=['email', 'name'], value=QueryFieldList.EXCLUDE
        )
        query += QueryFieldList(['email'], value=QueryFieldList.EXCLUDE)

        expect(query.as_dict()).to_be_like({})

    def test_only_query_field_list_and_exclude_id(self):
        query = QueryFieldList(
            ['name'], value=QueryFieldList.ONLY, _only_called=True
        ) + QueryFieldList(['_id'], value=QueryFieldList.EXCLUDE)

        expect(query.as_dict()).to_be_like({
            '_id': 0, 'name': 1
        })

    def test_slice_query_field_list(self):
        query = QueryFieldList(
            ['numbers'], value={'$slice': 10}, _only_called=False
        )

        expect(query.as_dict()).to_be_like({
            'numbers': {'$slice': 10}
        })

    def test_slice_and_always_include(self):
        query = (
            QueryFieldList(['numbers'], always_include=['numbers']) +
            QueryFieldList(
                ['numbers'], value={'$slice': 10}, _only_called=False
            )
        )

        expect(query.as_dict()).to_be_like({
            'numbers': {'$slice': 10}
        })

    def test_slice_with_only_and_exclude(self):
        query = (
            QueryFieldList() +
            QueryFieldList(
                ['numbers'], value={'$slice': 10}, _only_called=False
            ) + QueryFieldList(['numbers'], value=QueryFieldList.EXCLUDE)
        )

        expect(query.as_dict()).to_be_like({})

        # slice is assumed to act like only
        query = (
            QueryFieldList() +
            QueryFieldList(
                ['numbers'], value={'$slice': 10}, _only_called=False
            ) + QueryFieldList(
                ['name'], value=QueryFieldList.ONLY, _only_called=True
            )
        )

        expect(query.as_dict()).to_be_like({
            'name': 1, 'numbers': {'$slice': 10}
        })

        query = (
            QueryFieldList() +
            QueryFieldList(
                ['numbers'], value={'$slice': 10}, _only_called=False
            ) + QueryFieldList(
                ['name'], value={'$slice': 13}, _only_called=False
            )
        )

        expect(query.as_dict()).to_be_like({
            'numbers': {'$slice': 10}, 'name': {'$slice': 13}
        })

    def test_not_only_called_projection(self):
        query = (
            QueryFieldList() +
            QueryFieldList(
                ['name'], value=QueryFieldList.ONLY, _only_called=False
            )
        )

        expect(query.as_dict()).to_be_like({'name': 1})

    def test_wrong_value(self):
        query = (
            QueryFieldList(
                ['name'], value=QueryFieldList.ONLY, _only_called=False
            ) +
            QueryFieldList(
                ['name'], value='Wrong', _only_called=False
            )
        )

        expect(query.as_dict()).to_be_like({'name': 1})
