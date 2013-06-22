#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Database(object):
    def __init__(self, connection):
        self.connection = connection

    def ping(self, callback):
        self.connection.admin.command('ping', callback=callback)

    def __getattribute__(self, name):
        if name in ['ping', 'connection']:
            return object.__getattribute__(self, name)

        return getattr(self.connection, name)
