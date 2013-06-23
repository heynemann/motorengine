#!/usr/bin/env python
# -*- coding: utf-8 -*-

# code adapted from https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/base/metaclasses.py

from motorengine.fields import BaseField
from motorengine.errors import InvalidDocumentError
from motorengine.queryset.manager import QuerySetManager


class DocumentMetaClass(type):
    def __new__(cls, name, bases, attrs):
        flattened_bases = cls._get_bases(bases)
        super_new = super(DocumentMetaClass, cls).__new__

        # If a base class just call super
        metaclass = attrs.get('my_metaclass')
        if metaclass and issubclass(metaclass, DocumentMetaClass):
            return super_new(cls, name, bases, attrs)

        attrs['_is_document'] = attrs.get('_is_document', False)

        # EmbeddedDocuments could have meta data for inheritance
        if 'meta' in attrs:
            attrs['_meta'] = attrs.pop('meta')

        # EmbeddedDocuments should inherit meta data
        if '_meta' not in attrs:
            meta = MetaDict()
            for base in flattened_bases[::-1]:
                # Add any mixin metadata from plain objects
                if hasattr(base, 'meta'):
                    meta.merge(base.meta)
                elif hasattr(base, '_meta'):
                    meta.merge(base._meta)
            attrs['_meta'] = meta

        doc_fields = {}
        for base in flattened_bases[::-1]:
            if hasattr(base, '_fields'):
                doc_fields.update(base._fields)

            # Standard object mixin - merge in any Fields
            if not hasattr(base, '_meta'):
                base_fields = {}
                for attr_name, attr_value in base.__dict__.items():
                    if not isinstance(attr_value, BaseField):
                        continue
                    attr_value.name = attr_name
                    if not attr_value.db_field:
                        attr_value.db_field = attr_name
                    base_fields[attr_name] = attr_value

                doc_fields.update(base_fields)

        # Discover any document fields
        field_names = {}
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
            new_class._meta['collection'] = new_class.__name__

        if 'objects' not in dir(new_class):
            new_class.objects = QuerySetManager()

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


class MetaDict(dict):
    """Custom dictionary for meta classes.
    Handles the merging of set indexes
    """
    _merge_options = ('indexes',)

    def merge(self, new_options):
        for k, v in new_options.items():
            if k in self._merge_options:
                self[k] = self.get(k, []) + v
            else:
                self[k] = v
