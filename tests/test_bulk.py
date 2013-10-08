#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from preggy import expect
from tornado.testing import gen_test

from motorengine import (
    Document, StringField
)
from tests import AsyncTestCase


class Comment(Document):
    __collection__ = "CommentBulk"
    text = StringField(required=True)


class TestBulkInsert(AsyncTestCase):
    def setUp(self):
        super(TestBulkInsert, self).setUp()
        self.drop_coll("CommentBulk")

    @gen_test
    def test_can_insert_in_bulk(self):
        comments = [
            Comment(text=str(number))
            for number in range(100)
        ]

        yield Comment.objects.bulk_insert(comments)

        count = yield Comment.objects.count()

        expect(count).to_equal(100)

        for comment in comments:
            expect(comment._id).not_to_be_null()

    @gen_test
    def test_cant_insert_wrong_document_in_bulk(self):
        class OtherDoc(Document):
            pass

        comments = [
            OtherDoc()
        ]

        try:
            yield Comment.objects.bulk_insert(comments)
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of(
                "Validation for document 0 in the documents you are saving failed with: "
                "This queryset for class 'Comment' can't save an instance of type 'OtherDoc'."
            )
        else:
            assert False, "Should not have gotten this far"

    @gen_test
    def test_cant_insert_invalid_document_in_bulk(self):
        comments = [
            Comment(text=None)
        ]

        try:
            yield Comment.objects.bulk_insert(comments)
        except ValueError:
            err = sys.exc_info()[1]
            expect(err).to_have_an_error_message_of(
                "Validation for document 0 in the documents you are saving failed with: "
                "Field 'text' is required."
            )
        else:
            assert False, "Should not have gotten this far"
