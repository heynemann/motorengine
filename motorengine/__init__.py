#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.2.7'

try:
    from pymongo import ASCENDING, DESCENDING  # NOQA

    from motorengine.connection import connect, disconnect  # NOQA
    from motorengine.document import Document  # NOQA

    from motorengine.fields import (  # NOQA
        BaseField, StringField, BooleanField, DateTimeField,
        UUIDField, ListField, EmbeddedDocumentField, ReferenceField, URLField,
        EmailField, IntField, FloatField, DecimalField, BinaryField,
        JsonField
    )
except ImportError:  # NOQA
    pass  # likely setup.py trying to import version
