#!/usr/bin/env python
# -*- coding: utf-8 -*-

from easydict import EasyDict as edict
from tornado.concurrent import return_future


class BaseAggregation(object):
    def __init__(self, field, alias):
        self._field = field
        self.alias = alias

    @property
    def field(self):
        return self._field


class PipelineOperation(object):
    def __init__(self, aggregation):
        self.aggregation = aggregation

    def to_query(self):
        return {}


class GroupBy(PipelineOperation):
    def __init__(self, aggregation, *groups):
        super(GroupBy, self).__init__(aggregation)
        self.groups = groups

    def to_query(self):
        group_obj = {'$group': {'_id': {}}}

        for group in self.groups:
            if isinstance(group, BaseAggregation):
                group_obj['$group'].update(group.to_query(self.aggregation.queryset))
                continue

            field_name = self.aggregation.get_field(group).db_field
            group_obj['$group']['_id'][field_name] = "$%s" % field_name

        return group_obj


class Unwind(PipelineOperation):
    def __init__(self, aggregation, field):
        super(Unwind, self).__init__(aggregation)
        self.field = self.aggregation.get_field(field)

    def to_query(self):
        return {'$unwind': '$%s' % self.field.db_field}


class Aggregation(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self.pipeline = []
        self.ids = []

    def get_field(self, field):
        return field

    def group_by(self, *args):
        self.pipeline.append(GroupBy(self, *args))
        return self

    def unwind(self, field):
        self.pipeline.append(Unwind(self, field))
        return self

    def fill_ids(self, item):
        if not '_id' in item:
            return

        for id_name, id_value in item['_id'].items():
            item[id_name] = id_value

    def handle_aggregation(self, callback):
        def handle(*arguments, **kw):
            if arguments[1]:
                raise RuntimeError('Aggregation failed due to: %s' % str(arguments[1]))

            results = []
            for item in arguments[0]['result']:
                self.fill_ids(item)
                results.append(edict(item))

            callback(results)

        return handle

    @return_future
    def fetch(self, callback=None, alias=None):
        coll = self.queryset.coll(alias)
        coll.aggregate(self.to_query(), callback=self.handle_aggregation(callback))

    @classmethod
    def avg(cls, field, alias=None):
        from motorengine.aggregation.avg import AverageAggregation
        return AverageAggregation(field, alias)

    def to_query(self):
        query = []

        for group in self.pipeline:
            query.append(group.to_query())

        return query
