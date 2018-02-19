#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.0.0'

try:
    from pymongo import ASCENDING, DESCENDING  # NOQA

    from motorengine.connection import connect, disconnect  # NOQA
    from motorengine.document import Document  # NOQA

    from motorengine.fields import (  # NOQA
        BaseField, StringField, BooleanField, DateTimeField,
        UUIDField, ListField, EmbeddedDocumentField, ReferenceField, URLField,
        EmailField, IntField, FloatField, DecimalField, BinaryField,
        JsonField, ObjectIdField
    )

    from motorengine.aggregation.base import Aggregation  # NOQA
    from motorengine.query_builder.node import Q, QNot  # NOQA

except ImportError as e:  # NOQA
    # likely setup.py trying to import version
    import sys
    import traceback
    traceback.print_exception(*sys.exc_info())
