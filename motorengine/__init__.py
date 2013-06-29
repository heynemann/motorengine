#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

from pymongo import ASCENDING, DESCENDING  # NOQA
from motorengine.connection import connect, disconnect  # NOQA
from motorengine.document import Document  # NOQA

from motorengine.fields import (  # NOQA
    BaseField, StringField, BooleanField, DateTimeField
)
