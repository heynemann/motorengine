#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections

from motorengine.query.base import QueryOperator
from motorengine.query.exists import ExistsQueryOperator
from motorengine.query.greater_than import GreaterThanQueryOperator
from motorengine.query.greater_than_or_equal import GreaterThanOrEqualQueryOperator
from motorengine.query.lesser_than import LesserThanQueryOperator
from motorengine.query.lesser_than_or_equal import LesserThanOrEqualQueryOperator
from motorengine.query.in_operator import InQueryOperator
from motorengine.query.is_null import IsNullQueryOperator
from motorengine.query.not_operator import NotOperator
from motorengine.query.not_equal import NotEqualQueryOperator

from motorengine.query.contains import ContainsOperator
from motorengine.query.ends_with import EndsWithOperator
from motorengine.query.exact import ExactOperator
from motorengine.query.starts_with import StartsWithOperator
from motorengine.query.i_contains import IContainsOperator
from motorengine.query.i_ends_with import IEndsWithOperator
from motorengine.query.i_exact import IExactOperator
from motorengine.query.i_starts_with import IStartsWithOperator


OPERATORS = {
    'exists': ExistsQueryOperator,
    'gt': GreaterThanQueryOperator,
    'gte': GreaterThanOrEqualQueryOperator,
    'lt': LesserThanQueryOperator,
    'lte': LesserThanOrEqualQueryOperator,
    'in': InQueryOperator,
    'is_null': IsNullQueryOperator,
    'ne': NotEqualQueryOperator,
    'not': NotOperator,
    'contains': ContainsOperator,
    'endswith': EndsWithOperator,
    'exact': ExactOperator,
    'startswith': StartsWithOperator,
    'icontains': IContainsOperator,
    'iendswith': IEndsWithOperator,
    'iexact': IExactOperator,
    'istartswith': IStartsWithOperator,
}


class DefaultOperator(QueryOperator):
    def to_query(self, field_name, value):
        return {
            field_name: value
        }


# from http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def transform_query(document, **query):
    mongo_query = {}

    for key, value in sorted(query.items()):
        if key == 'raw':
            update(mongo_query, value)
            continue

        if '__' not in key:
            field = document.get_fields(key)[0]
            field_name = field.db_field
            operator = DefaultOperator()
            field_value = operator.get_value(field, value)
        else:
            values = key.split('__')
            field_reference_name, operator = ".".join(values[:-1]), values[-1]
            if operator not in OPERATORS:
                field_reference_name = "%s.%s" % (field_reference_name, operator)
                operator = ""

            fields = document.get_fields(field_reference_name)

            field_name = ".".join([
                hasattr(field, 'db_field') and field.db_field or field
                for field in fields
            ])
            operator = OPERATORS.get(operator, DefaultOperator)()
            field_value = operator.get_value(fields[-1], value)

        update(mongo_query, operator.to_query(field_name, field_value))

    return mongo_query


def validate_fields(document, query):
    from motorengine.fields.embedded_document_field import EmbeddedDocumentField
    from motorengine.fields.list_field import ListField

    for key, query in sorted(query.items()):
        if '__' not in key:
            fields = document.get_fields(key)
            operator = "equals"
        else:
            values = key.split('__')
            field_reference_name, operator = ".".join(values[:-1]), values[-1]
            if operator not in OPERATORS:
                field_reference_name = "%s.%s" % (field_reference_name, operator)
                operator = ""

            fields = document.get_fields(field_reference_name)

        is_none = (not fields) or (not all(fields))
        is_embedded = isinstance(fields[0], (EmbeddedDocumentField,))
        is_list = isinstance(fields[0], (ListField,))

        if is_none or (not is_embedded and not is_list and operator == ''):
            raise ValueError(
                "Invalid filter '%s': Invalid operator (if this is a sub-property, "
                "then it must be used in embedded document fields)." % key)


def transform_field_list_query(document, query_field_list):
    if not query_field_list:
        return None

    fields = {}
    for key in query_field_list.keys():
        if key == '_id':
            fields[key] = query_field_list[key]
        else:
            fields_chain = document.get_fields(key)
            field_db_name = '.'.join([field.db_field for field in fields_chain])
            fields[field_db_name] = query_field_list[key]

    return fields
