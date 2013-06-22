#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Database(object):
    def __init__(self, connection, database):
        self.connection = connection
        self.database = database

    def ping(self, callback):
        self.connection.admin.command('ping', callback=callback)

    def disconnect(self):
        return self.connection.disconnect()

    def __getattribute__(self, name):
        if name in ['ping', 'connection', 'database', 'disconnect']:
            return object.__getattribute__(self, name)

        return getattr(self.database, name)

    def __getitem__(self, val):
        return getattr(self.database, val)
