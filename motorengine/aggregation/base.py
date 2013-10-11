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
    def __init__(self, queryset, group, project=None, unwind=None):
        self.queryset = queryset
        self.group = group
        self.project = project
        self.unwind = unwind
        self.ids = []

    def fill_ids(self, item):
        for id_index, id_name in enumerate(self.ids):
            if isinstance(item['_id'], (tuple, list, set)):
                item[id_name] = item['_id'][id_index]
            elif isinstance(item['_id'], (dict,)):
                item[id_name] = item['_id'][id_name]
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
        ]

        group_obj = {'$group': {'_id': None}}

        self.ids = []
        projections = []

        for group in self.group:
            if isinstance(group, BaseAggregation):
                group_obj['$group'].update(group.to_query(self.queryset))
                projections.append(group.field.db_field)
                continue

            field_name = self.get_field(group).db_field
            self.ids.append(field_name)
            projections.append(field_name)

        # TODO: RAISE IF NO ID

        if len(self.ids) == 1:
            group_obj['$group']['_id'] = "$%s" % self.ids[0]
        else:
            group_obj['$group']['_id'] = dict([(name, "$%s" % name) for name in self.ids])

        if self.project is None:
            project_obj = {
                "$project": dict([(field_name, 1) for field_name in projections])
            }

            query.append(project_obj)

        if self.unwind is not None:
            unwind_obj = {
                "$unwind": "$%s" % self.get_field(self.unwind).db_field
            }

            query.append(unwind_obj)

        query.append(group_obj)

        return query
