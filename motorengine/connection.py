#!/usr/bin/env python
# -*- coding: utf-8 -*-

# code adapted from https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/connection.py

import sys

try:
    import six
except ImportError:
    pass

try:
    from motor import MotorClient, MotorReplicaSetClient
except ImportError:
    pass

from motorengine.database import Database

DEFAULT_CONNECTION_NAME = 'default'


class ConnectionError(Exception):
    pass


_connection_settings = {}
_connections = {}


def register_connection(alias, **kwargs):
    global _connection_settings

    _connection_settings[alias] = kwargs


def cleanup():
    global _connections
    global _connection_settings

    _connections = {}
    _connection_settings = {}


def disconnect(alias=DEFAULT_CONNECTION_NAME):
    global _connections
    global _connections_settings

    if alias in _connections:
        get_connection(alias=alias).disconnect()
        del _connections[alias]
        del _connection_settings[alias]


def get_connection(alias=DEFAULT_CONNECTION_NAME):
    global _connections

    if alias not in _connections:
        conn_settings = _connection_settings[alias].copy()

        connection_class = MotorClient
        if 'replicaSet' in conn_settings:
            connection_class = MotorReplicaSetClient
            conn_settings['hosts_or_uri'] = conn_settings.pop('host', None)

            # Discard port since it can't be used on MongoReplicaSetClient
            conn_settings.pop('port', None)

            # Discard replicaSet if not base string
            if not isinstance(conn_settings['replicaSet'], six.string_types):
                conn_settings.pop('replicaSet', None)

        try:
            _connections[alias] = connection_class(**conn_settings)
            _connections[alias].open_sync()
        except Exception:
            exc_info = sys.exc_info()[1]
            raise ConnectionError("Cannot connect to database %s :\n%s" % (alias, exc_info))

    return Database(_connections[alias])


def connect(alias=DEFAULT_CONNECTION_NAME, **kwargs):
    """Connect to the database specified by the 'db' argument.

    Connection settings may be provided here as well if the database is not
    running on the default port on localhost. If authentication is needed,
    provide username and password arguments as well.

    Multiple databases are supported by using aliases.  Provide a separate
    `alias` to connect to a different instance of :program:`mongod`.
    """
    global _connections
    if alias not in _connections:
        register_connection(alias, **kwargs)

    return get_connection(alias)
