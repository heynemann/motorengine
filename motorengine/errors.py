#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


class InvalidDocumentError(ValueError):
    pass


class LoadReferencesRequiredError(RuntimeError):
    pass


class PartlyLoadedDocumentError(ValueError):
    pass


# E11000 duplicate key error index: test.UniqueFieldDocument.$name_1  dup key: { : "test" }
PYMONGO_ERROR_REGEX = re.compile(r"(?P<error_code>.+?)\s(?P<error_type>.+?):\s*(?P<index_name>.+?)\s+(?P<error>.+?)")


class UniqueKeyViolationError(RuntimeError):
    def __init__(self, message, error_code, error_type, index_name, instance_type):
        super(UniqueKeyViolationError, self).__init__(message)

        self.error_code = error_code
        self.error_type = error_type
        self.index_name = index_name
        self.instance_type = instance_type

    def __str__(self):
        return "The index \"%s\" was violated when trying to save this \"%s\" (error code: %s)." % (
            self.index_name,
            self.instance_type.__name__,
            self.error_code
        )

    @classmethod
    def from_pymongo(self, err, instance_type):
        match = PYMONGO_ERROR_REGEX.match(err)

        if not match:
            return None

        groups = match.groupdict()

        return UniqueKeyViolationError(
            message=err, error_code=groups['error_code'], error_type=groups['error_type'],
            index_name=groups['index_name'], instance_type=instance_type
        )
