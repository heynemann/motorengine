#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint

from preggy import expect

from motorengine import (
    Document, StringField, BooleanField, ListField,
    DESCENDING, DateTimeField, IntField, Aggregation
)
from tests import AsyncTestCase

AVAILABLE_STATES = ['ny', 'ca', 'wa', 'fl']
CITIES = ['New York', 'San Francisco', 'Washington', 'Orlando']


class City(Document):
    __collection__ = "AggregationCity"

    city = StringField()
    state = StringField()
    pop = IntField()


class User(Document):
    __collection__ = "AggregationUser"

    email = StringField(required=True)
    first_name = StringField(max_length=50, default=lambda: "Bernardo")
    last_name = StringField(max_length=50, default="Heynemann")
    is_admin = BooleanField(default=True)
    updated_at = DateTimeField(required=True, auto_now_on_insert=True, auto_now_on_update=True)
    number_of_documents = IntField()
    list_items = ListField(IntField())


class TestAggregation(AsyncTestCase):
    def setUp(self):
        super(TestAggregation, self).setUp()
        self.drop_coll("AggregationUser")
        self.drop_coll("AggregationCity")
        self.add_users()
        self.add_cities()

    def add_users(self):
        users = []
        for i in range(100):
            users.append(User(
                email="heynemann@gmail.com",
                first_name="Bernardo%d" % i,
                last_name="Heynemann%d" % i,
                is_admin=i % 2 == 0,
                number_of_documents=i * 100,
                list_items=list(range(i)),
            ))

        User.objects.bulk_insert(users, callback=self.stop)
        self.wait()

    def add_cities(self):
        cities = []
        for i in range(500):
            city_index = randint(0, 3)
            city_name = CITIES[city_index]
            state_name = AVAILABLE_STATES[city_index]

            cities.append(City(
                city=city_name,
                state=state_name,
                pop=randint(10000, 50000)
            ))

        City.objects.bulk_insert(cities, callback=self.stop)
        self.wait()

    def test_can_aggregate_number_of_documents(self):
        User.objects.aggregate.group_by(
            User.email,
            Aggregation.avg(User.number_of_documents, alias="number_of_documents")
        ).fetch(
            callback=self.stop
        )

        result = self.wait()

        expect(result).not_to_be_null()
        expect(result).to_length(1)
        expect(result[0].email).to_equal('heynemann@gmail.com')
        expect(result[0].number_of_documents).to_be_like(4950.0)

    def test_can_aggregate_with_unwind(self):
        User.objects.aggregate.unwind(User.list_items).group_by(
            User.email,
            User.list_items,
            Aggregation.avg(User.number_of_documents, alias="number_of_documents")
        ).fetch(callback=self.stop)

        result = self.wait()

        expect(result).not_to_be_null()
        expect(result).to_length(99)
        expect(result[0].email).to_equal('heynemann@gmail.com')
        expect(result[0].list_items).to_be_numeric()
        expect(result[0].number_of_documents).to_be_numeric()

    def test_can_aggregate_with_sorting(self):
        User.objects.aggregate.order_by(User.number_of_documents, DESCENDING).fetch(callback=self.stop)

        result = self.wait()

        expect(result).not_to_be_null()
        expect(result).to_length(100)
        for i in range(100):
            expect(result[i].number_of_documents).to_equal((99 - i) * 100)

    # TODO: Remove aggregation support
    #def test_can_aggregate_city_data(self):
        #City.objects.aggregate.group_by(
            #City.state,
            #Aggregation.sum(City.pop, alias="totalPop")
        #).match(
            #totalPop__gte=1000 * 1000
        #).fetch(callback=self.stop)

        #result = self.wait()

        #expect(result).not_to_be_null()
        #expect(result).to_length(4)

    def test_can_average_city_population(self):
        City.objects.aggregate.group_by(
            City.state,
            City.city,
            Aggregation.sum(City.pop, alias="total_pop")
        ).group_by(
            City.state,
            Aggregation.avg("total_pop", alias="avg_pop")
        ).fetch(callback=self.stop)

        results = self.wait()

        expect(results).not_to_be_null()
        expect(results).to_length(4)

        states = [result.state for result in results]

        expect(states).to_be_like(['ny', 'ca', 'wa', 'fl'])

        for state in results:
            expect(state.avg_pop).to_be_greater_than(2000000)

    def test_can_average_city_population_by_raw_query(self):
        City.objects.aggregate.raw([
            {
                '$group': {
                    '_id': {'state': '$state', 'city': '$city'},
                    'pop': {'$sum': '$pop'}
                }
            },
            {
                '$group': {
                    '_id': '$_id.state',
                    'avgCityPop': {
                        '$avg': '$pop'
                    }
                }
            }
        ]).fetch(callback=self.stop)

        results = self.wait()

        expect(results).not_to_be_null()
        expect(results).to_length(4)

        states = [result._id for result in results]

        expect(states).to_be_like(['ny', 'ca', 'wa', 'fl'])

        for state in results:
            expect(state.avgCityPop).to_be_greater_than(2000000)
