#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseField(object):
    '''
    This class is the base to all fields. This is not supposed to be used directly in documents.

    Available arguments:

    * `db_field` - The name this field will have when sent to MongoDB
    * `default` - The default value (or callable) that will be used when first creating an instance that has no value set for the field
    * `required` - Indicates that if the field value evaluates to empty (using the `is_empty` method) a validation error is raised
    * `on_save` - A function of the form `lambda doc, creating` that is called right before sending the document to the DB.
    * `unique` - Indicates whether an unique index should be created for this field.
    * `sparse` - Indicates whether a sparse index should be created for this field. This also will not pass empty values to DB.

    To create a new field, four methods can be overwritten:

    * `is_empty` - Indicates that the field is empty (the default is comparing the value to None);
    * `validate` - Returns if the specified value for the field is valid;
    * `to_son` - Converts the value to the BSON representation required by motor;
    * `from_son` - Parses the value from the BSON representation returned from motor.
    '''

    total_creation_counter = 0

    def __init__(self, db_field=None, default=None, required=False, on_save=None, unique=None, sparse=False):
        global creation_counter
        self.creation_counter = BaseField.total_creation_counter
        BaseField.total_creation_counter += 1

        self.db_field = db_field
        self.required = required
        self.default = default
        self.on_save = on_save
        self.unique = unique
        self.sparse = sparse

    def is_empty(self, value):
        return value is None

    def get_value(self, value):
        return value

    def to_son(self, value):
        return value

    def to_query(self, value):
        return self.to_son(value)

    def from_son(self, value):
        return value

    def validate(self, value):
        return True
