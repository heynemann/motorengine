#!/usr/bin/env python
# -*- coding: utf-8 -*-

# code adapted from https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/base/metaclasses.py

from motorengine.fields import BaseField
from motorengine.errors import InvalidDocumentError
from motorengine.queryset import QuerySet


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class DocumentMetaClass(type):
    def __new__(cls, name, bases, attrs):
        flattened_bases = cls._get_bases(bases)
        super_new = super(DocumentMetaClass, cls).__new__

        doc_fields = {}
        for base in flattened_bases[::-1]:
            if hasattr(base, '_fields'):
                doc_fields.update(base._fields)

        # Discover any document fields
        field_names = {}

        for field_name, doc_field in doc_fields.items():
            field_names[doc_field.db_field] = field_names.get(
                doc_field.db_field, 0) + 1

        for attr_name, attr_value in attrs.items():
            if not isinstance(attr_value, BaseField):
                continue
            attr_value.name = attr_name
            if not attr_value.db_field:
                attr_value.db_field = attr_name
            doc_fields[attr_name] = attr_value

            # Count names to ensure no db_field redefinitions
            field_names[attr_value.db_field] = field_names.get(
                attr_value.db_field, 0) + 1

        # Ensure no duplicate db_fields
        duplicate_db_fields = [k for k, v in field_names.items() if v > 1]
        if duplicate_db_fields:
            msg = ("Multiple db_fields defined for: %s " %
                   ", ".join(duplicate_db_fields))
            raise InvalidDocumentError(msg)

        # Set _fields and db_field maps
        attrs['_fields'] = doc_fields
        attrs['_db_field_map'] = dict([(k, getattr(v, 'db_field', k))
                                      for k, v in doc_fields.items()])
        attrs['_fields_ordered'] = tuple(i[1] for i in sorted(
                                         (v.creation_counter, v.name)
                                         for v in doc_fields.values()))
        attrs['_reverse_db_field_map'] = dict(
            (v, k) for k, v in attrs['_db_field_map'].items())

        new_class = super_new(cls, name, bases, attrs)

        if not '__collection__' in attrs:
            new_class.__collection__ = new_class.__name__

        if not '__lazy__' in attrs:
            new_class.__lazy__ = True

        if not '__alias__' in attrs:
            new_class.__alias__ = None

        setattr(new_class, 'objects', classproperty(lambda *args, **kw: QuerySet(new_class)))

        return new_class

    @classmethod
    def _get_bases(cls, bases):
        if isinstance(bases, BasesTuple):
            return bases
        seen = []
        bases = cls.__get_bases(bases)
        unique_bases = (b for b in bases if not (b in seen or seen.append(b)))
        return BasesTuple(unique_bases)

    @classmethod
    def __get_bases(cls, bases):
        for base in bases:
            if base is object:
                continue
            yield base
            for child_base in cls.__get_bases(base.__bases__):
                yield child_base


class BasesTuple(tuple):
    """Special class to handle introspection of bases tuple in __new__"""
    pass
