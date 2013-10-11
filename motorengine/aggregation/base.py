#!/usr/bin/env python
# -*- coding: utf-8 -*-

from easydict import EasyDict as edict


class BaseAggregation(object):
    def __init__(self, field, alias):
        self._field = field
        self.alias = alias

    @property
    def field(self):
        return self._field


class Aggregation(object):
    def __init__(self, queryset, group):
        self.queryset = queryset
        self.group = group
        self.ids = []

    def fill_ids(self, item):
        for id_index, id_name in enumerate(self.ids):
            if isinstance(item['_id'], (tuple, list, set)):
                item[id_name] = item['_id'][id_index]
            else:
                item[id_name] = item['_id']

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

    @classmethod
    def avg(cls, field, alias=None):
        from motorengine.aggregation.avg import AverageAggregation
        return AverageAggregation(field, alias)

    def get_field(self, field):
        return field

    def to_query(self):
        query = [
            {'$group': {'_id': None}}
        ]

        self.ids = []

        for group in self.group:
            if isinstance(group, BaseAggregation):
                query[0]['$group'].update(group.to_query(self.queryset))
                continue

            field_name = self.get_field(group).db_field
            self.ids.append(field_name)

        # TODO: RAISE IF NO ID

        if len(self.ids) == 1:
            query[0]['$group']['_id'] = "$%s" % self.ids[0]
        else:
            query[0]['$group']['_id'] = dict([(name, "$%s" % name) for name in self.ids])

        return query
