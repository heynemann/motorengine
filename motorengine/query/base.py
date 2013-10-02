#!/usr/bin/env python
# -*- coding: utf-8 -*-


class QueryOperator(object):
    def __init__(self, value):
        self.value = value

    def to_query(self):
        raise NotImplementedError()
