#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

# Adapted from https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/queryset/visitor.py

from motorengine.query_builder.transform import transform_query


class QNodeVisitor(object):
    """Base visitor class for visiting Q-object nodes in a query tree.
    """

    def visit_combination(self, combination):
        """Called by QCombination objects.
        """
        return combination

    def visit_query(self, query):
        """Called by (New)Q objects.
        """
        return query


class DuplicateQueryConditionsError(RuntimeError):
    pass


class SimplificationVisitor(QNodeVisitor):
    """Simplifies query trees by combinging unnecessary 'and' connection nodes
    into a single Q-object.
    """

    def visit_combination(self, combination):
        if combination.operation == combination.AND:
            # The simplification only applies to 'simple' queries
            if all(isinstance(node, Q) for node in combination.children):
                queries = [n.query for n in combination.children]
                try:
                    return Q(**self._query_conjunction(queries))
                except DuplicateQueryConditionsError:
                    # Cannot be simplified
                    pass
        return combination

    def _query_conjunction(self, queries):
        """Merges query dicts - effectively &ing them together.
        """
        query_ops = set()
        combined_query = {}
        for query in queries:
            ops = set(query.keys())
            # Make sure that the same operation isn't applied more than once
            # to a single field
            intersection = ops.intersection(query_ops)
            if intersection:
                raise DuplicateQueryConditionsError()

            query_ops.update(ops)
            combined_query.update(copy.deepcopy(query))
        return combined_query


class QueryCompilerVisitor(QNodeVisitor):
    """Compiles the nodes in a query tree to a PyMongo-compatible query
    dictionary.
    """

    def __init__(self, document):
        self.document = document

    def visit_combination(self, combination):
        operator = "$and"
        if combination.operation == combination.OR:
            operator = "$or"

        return {operator: combination.children}

    def visit_query(self, query):
        return transform_query(self.document, **query.query)


class QNode(object):
    """Base class for nodes in query trees.
    """

    AND = 0
    OR = 1

    def to_query(self, document):
        query = self.accept(SimplificationVisitor(), document)
        query = query.accept(QueryCompilerVisitor(document), document)
        return query

    def accept(self, visitor, document):
        raise NotImplementedError

    def _combine(self, other, operation):
        """Combine this node with another node into a QCombination object.
        """
        if getattr(other, 'empty', True):
            return self

        if self.empty:
            return other

        return QCombination(operation, [self, other])

    @property
    def empty(self):
        return False

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        return QNot(self)


class QCombination(QNode):
    """Represents the combination of several conditions by a given logical
    operator.
    """

    def __init__(self, operation, children):
        self.operation = operation
        self.children = []
        for node in children:
            # If the child is a combination of the same type, we can merge its
            # children directly into this combinations children
            if isinstance(node, QCombination) and node.operation == operation:
                self.children += node.children
            else:
                self.children.append(node)

    def accept(self, visitor, document):
        for i in range(len(self.children)):
            if isinstance(self.children[i], QNode):
                self.children[i] = self.children[i].accept(visitor, document)

        return visitor.visit_combination(self)

    @property
    def empty(self):
        return not bool(self.children)


class Q(QNode):
    """
    A simple query object, used in a query tree to build up more complex query structures.

    .. testsetup:: querying_with_Q

        import tornado.ioloop
        from motorengine import *

        class User(Document):
            __collection__ = "UserQueryingWithQ"
            name = StringField()
            age = IntField()

        io_loop = tornado.ioloop.IOLoop.instance()
        connect("test", host="localhost", port=27017, io_loop=io_loop)

    .. testcode:: querying_with_Q

        def handle_users_found(users):
            try:
                assert users[0].name == "Bernardo"
            finally:
                io_loop.stop()

        def handle_user_created(user):
            query = Q(name="Bernardo") | Q(age__gt=30)
            users = User.objects.filter(query).find_all(callback=handle_users_found)

        def create_user():
            user = User(name="Bernardo", age=32)
            user.save(callback=handle_user_created)

        io_loop.add_timeout(1, create_user)
        io_loop.start()
    """

    def __init__(self, *arguments, **query):
        if arguments and len(arguments) == 1 and isinstance(arguments[0], dict):
            self.query = {"raw": arguments[0]}
        else:
            self.query = query

    def accept(self, visitor, document):
        return visitor.visit_query(self)

    @property
    def empty(self):
        return not bool(self.query)


class QNot(QNode):
    def __init__(self, query):
        self.query = query

    def accept(self, visitor, document):
        return self.to_query(document)

    def to_query(self, document):
        query = self.query.to_query(document)
        result = {}
        for key, value in query.items():
            if isinstance(value, (dict, )):
                result[key] = {
                    "$not": value
                }
            elif isinstance(value, (tuple, set, list)):
                result[key] = {
                    "$nin": value
                }
            else:
                result[key] = {
                    "$ne": value
                }

        return result
