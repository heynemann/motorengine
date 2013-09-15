#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseField(object):
    '''
    This class is the base to all fields. This is not supposed to be used directly in documents.

    Available arguments:

    * `db_field` - The name this field will have when sent to MongoDB
    * `default` - The default value (or callable) that will be used when first creating an instance that has no value set for the field
    * `required` - Indicates that if the field value evaluates to empty (using the `is_empty` method) a validation error is raised

    To create a new field, four methods can be overwritten:

    * `is_empty` - Indicates that the field is empty (the default is comparing the value to None);
    * `validate` - Returns if the specified value for the field is valid;
    * `to_son` - Converts the value to the BSON representation required by motor;
    * `from_son` - Parses the value from the BSON representation returned from motor.
    '''

    total_creation_counter = 0

    def __init__(self, db_field=None, default=None, required=False):
        global creation_counter
        self.creation_counter = BaseField.total_creation_counter
        BaseField.total_creation_counter += 1

        self.db_field = db_field
        self.required = required
        self.default = default

    def is_empty(self, value):
        return value is None

    def to_son(self, value):
        return value

    def from_son(self, value):
        return value

    def validate(self, value):
        return True
