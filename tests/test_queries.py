"""Test Queries

This module contains the queries test case for the Squirrel program.

Examples
    python -m unittest tests.test_queries
"""
import string
import random
import unittest
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient

from squirrel.queries import *
from squirrel.schemas import *
from squirrel.helpers import *
from squirrel.squirrel import *


class QueriesTest(unittest.TestCase):
    def setUp(self):
        self.initial_item = {
            "name":"Dunston",
            "species":"Chimpanzee",
            "favoriteFoods": [
                "bananas",
                "eggs"
            ],
            "owner": {
                "name": "John",
                "age": 12,
                "contact":4328792,
                "address": "Suite 4 Trump Towers"
            }
        }
        
        self.other_item = {
            "name": "Pete",
            "species": "Parrot",
            "favoriteFoods": [
                "apple",
                "mango"
            ],
            "owner": {
                "name": "Randy",
                "age": 64,
                "contact": 8415932,
                "address": "199 Thomas Street"
            }
        }

        self.next_item = {
            "name": "Marley",
            "species": "Parrot",
            "favoriteFoods": [
                "table scraps",
                "hot sauce"
            ],
            "owner": {
                "name": "Clementine",
                "age": 13,
                "contact": 8104326,
                "address": "12 Baleview Avenue"
            }
        }

        self.function = {
            'name': 'dummyfunc',
            'type': 'function',
            'versions': [
                {
                    'docstring': 'Returns True always',
                    'source': (
                        "def dummyfunc():\n"
                        "\"\"\"Returns True always\"\"\"\n"
                        "    return 1"
                    ),
                    'created': datetime.today().replace(microsecond=0),
                    'version_name': 'default'
                },
                {
                    'docstring': 'Returns non zero value',
                    'source': (
                        "def dummyfunc():\n"
                        "\"\"\"Returns non zero value\"\"\"\n"
                        "    return 99"
                    ),
                    'created': datetime.today().replace(microsecond=0),
                    'version_name': 'dummyfunc-non-zero'
                }
            ]
        }

        self.function2 = {
            'name': 'hello',
            'type': 'function',
            'versions': [
                {
                    'docstring': 'Says hello',
                    'source': (
                        "def hello():\n"
                        "\"\"\"Says hello\"\"\"\n"
                        "    print(\"hello\")"
                    ),
                    'created': datetime.today().replace(microsecond=0),
                    'version_name': 'default'
                }
            ]
        }

        self.new_version = {
            'docstring': 'Returns non zero value',
            'source': (
                "def dummyfunc():\n"
                "\"\"\"Returns non zero value\"\"\"\n"
                "    return 42"
            ),
            'created': datetime.today().replace(microsecond=0),
            'version_name': 'dummyfunc-non-zero-42'
        }

    def tearDown(self):
        self.delete_test_db(TEST_DB)

    def delete_test_db(self, db_name):
        client = MongoClient()
        client.drop_database(db_name)
        new_dbs = client.list_database_names()
        self.assertNotIn(db_name, new_dbs)

    def test_has_database(self):
        self.assertTrue(has_database('book'))
        name = ''.join(random.choice(string.ascii_lowercase)
                       for i in range(20))
        self.assertFalse(has_database(name))
    
    def test_has_client(self):
        self.assertTrue(has_client())

    def test_create_database(self):
        case = [
            {"name": "a", "number": 1}
        ]

        a = create_database('deleteme', 'deletes', case[0])
        self.assertIsNotNone(a)
        
        client = MongoClient()

        dbs = client.list_database_names()
        self.assertIn('deleteme', dbs)
        
        cols = client['deleteme'].list_collection_names()
        self.assertIn('deletes', cols)

    def test_insert_item(self):
        db = create_database('deleteme', 'pets', self.initial_item)
        pet = self.other_item
        
        i = insert_item('deleteme', 'pets', pet)
        self.assertEqual(type(i), ObjectId)
        self.assertEqual(len([_ for _ in db.pets.find()]), 2)
        
        item = db.pets.find_one(
            {"name": pet['name']}
        )

        self.assertEqual(item, pet, "match not found")
        self.delete_test_db('deleteme')

    def insert_many_items(self):
        pass
    
    def test_insert_unique_item(self):
        db = create_database('deleteme', 'pets', self.initial_item)
        a = insert_unique_item('deleteme', 'pets', self.initial_item)
        self.assertIsNone(a)
        b = insert_unique_item('deleteme', 'pets', self.other_item)
        self.assertIsNotNone(b)
        self.delete_test_db('deleteme')

    def test_item_exists(self):
        create_database('deleteme', 'pets', self.initial_item)
        self.assertFalse(item_exists('deleteme', 'pets', {'name': 'Jacob'}))
        self.assertTrue(item_exists('deleteme', 'pets', {'name': 'Dunston'}))
    
    def test_get_item(self):
        create_database('deleteme', 'pets', self.initial_item)
        pet = self.other_item

        i = insert_item('deleteme', 'pets', pet)
        self.assertEqual(type(i), ObjectId)

        res = get_item('deleteme', 'pets', pet)

        res = get_item('deleteme', 'pets', pet, **
                       {"_id": 0, "name": 1, "species": 1})
        
        self.assertEqual(res, filter_dict(pet, lambda elem: elem[0] in ['name', 'species']), "match not found")
        
        res = get_item('deleteme', 'pets', self.next_item, **
                       {"_id": 0, "name": 1, "species": 1})

        self.assertIsNone(res, "match found")
        
        self.delete_test_db('deleteme')

    def test_get_many_items(self):
        create_database('deleteme', 'pets', self.initial_item)        
        i = insert_item('deleteme', 'pets', self.other_item)
        self.assertEqual(type(i), ObjectId)

        res = get_many_items('deleteme', 'pets', **{"_id": 0, "name": 1, "species": 1})

        res = [_ for _ in res]

        self.assertEqual(len(res), 2)
        self.assertCountEqual(res, [{'name': 'Dunston', 'species': 'Chimpanzee'},
                                    {'name': 'Pete', 'species': 'Parrot'}])

        self.delete_test_db('deleteme')

    def test_get_all_items_in_collection(self):
        pass

    def test_update_item(self):
        create_database('deleteme', 'pets', self.initial_item)
        i = insert_item('deleteme', 'pets', self.other_item)
        
        self.assertEqual(type(i), ObjectId)

        pete = get_item('deleteme', 'pets', {"name": "Pete"}, **{"_id":0})
        self.assertEqual(pete['owner']['age'], 64)

        res = update_item('deleteme', 'pets', pete, {"owner": {"age": 65}})

        pete = get_item('deleteme', 'pets', {"name": "Pete"}, **{"_id":0})
        self.assertEqual(pete["owner"]["age"], 65)
        
        self.delete_test_db('deleteme')
    
    def test_update_many(self):
        create_database('deleteme', 'pets', self.initial_item)
        i = insert_item('deleteme', 'pets', self.other_item)
        j = insert_item('deleteme', 'pets', self.next_item)

        self.assertEqual(type(i), ObjectId)
        self.assertEqual(type(j), ObjectId)

        parrot_foods = ['awara', 'cashew', 'sugar cane']

        pete = get_item('deleteme', 'pets', {'name': 'Pete'}, **{'_id': 0})
        marley = get_item('deleteme', 'pets', {'name': 'Marley'}, **{'_id': 0})
        self.assertCountEqual(pete['favoriteFoods'], self.other_item['favoriteFoods'])
        self.assertCountEqual(marley['favoriteFoods'], self.next_item['favoriteFoods'])

        query = {'species': 'Parrot'}
        update_many('deleteme', 'pets', query, {
                    'favoriteFoods': parrot_foods})

        
        pete = get_item('deleteme', 'pets', {'name': 'Pete'}, **{'_id': 0})
        marley = get_item('deleteme', 'pets', {'name': 'Marley'}, **{'_id': 0})
        self.assertCountEqual(pete['favoriteFoods'], parrot_foods)
        self.assertCountEqual(marley['favoriteFoods'], parrot_foods)

        self.delete_test_db('deleteme')

    def test_insert_embedded_document(self):
        create_database(TEST_DB, 'functions', self.function)
        insert_embedded_document(
            TEST_DB,
            'functions',
            {"name": "dummyfunc"},
            {"versions": self.new_version}
        )
        state = get_all_items_in_collection(TEST_DB, 'functions')
        #print("STATE")
        #pprint(state)
        self.assertEqual(len(state), 1)
        ver_names = [ver['version_name'] for ver in state[0]['versions']]
        self.assertIn("dummyfunc-non-zero-42", ver_names)

    def test_find_one_and_update(self):
        create_database(TEST_DB, 'functions', self.function)
        item = get_item(TEST_DB, 'functions', {'name':'dummyfunc'}, **{'_id': 1})
        src = (
            "def dummyfunc():\n"
            "\"\"\"Returns two\"\"\"\n"
            "    return 1+1"
        )
        updated_docstring = update_item(
            TEST_DB,
            'functions',
            {
                "name": self.function['name'],
                "versions.version_name": "default"
            },
            {
                "versions.$.docstring": "Returns two"
            }
        )
        item = get_item(
            TEST_DB,
            'functions',
            {"name": self.function['name']},
            **{"versions": 1}
        )
        state = get_all_items_in_collection(TEST_DB, 'functions')
        #pprint(state)
        self.assertEqual(len(state), 1)
        for ver in item['versions']:
            if ver['version_name'] == 'default':
                result = ver['docstring']
                self.assertEqual(result, "Returns two")
        
        updated_source = update_item(
            TEST_DB,
            'functions',
            {
                "name": self.function['name'],
                "versions.version_name": "default"
            },
            {
                "versions.$.source": src
            }
        )

        state = get_all_items_in_collection(TEST_DB, 'functions')
        #pprint(state)
        self.assertEqual(len(state), 1)
        for ver in item['versions']:
            if ver['version_name'] == 'default':
                result = ver['docstring']
                self.assertEqual(result, "Returns two")        

    def test_add_field(self):
        create_database('deleteme', 'pets', self.initial_item)      
        i = insert_item('deleteme', 'pets', self.other_item)
        
        self.assertEqual(type(i), ObjectId)

        pete = get_item('deleteme', 'pets', {"name": "Pete"}, **{"_id":0})
        self.assertNotIn('age', pete.keys(), 'field already there!!')

        add_field('deleteme', 'pets', pete, {'age': 1})
        pete = get_item('deleteme', 'pets', {"name": "Pete"}, **{"_id":0})
        self.assertIn('age', pete.keys(), 'field not added!')
        
        self.delete_test_db('deleteme')
    
    def test_remove_one(self):
        db = create_database('deleteme', 'pets', self.initial_item)
        a = get_item('deleteme', 'pets', {"name": "Dunston"})
        self.assertEqual(type(a['_id']), ObjectId)

        remove_one('deleteme', 'pets', {"name": "Dunston"})

        a = get_item('deleteme', 'pets', {"name": "Dunston"})
        self.assertIsNone(a)
        self.delete_test_db('deleteme')
    
    def test_remove_many(self):
        db = create_database('deleteme', 'pets', self.initial_item)
        a = get_item('deleteme', 'pets', {"name": "Dunston"})
        self.assertEqual(type(a['_id']), ObjectId)

        remove_many('deleteme', 'pets', {})

        a = get_item('deleteme', 'pets', {"name": "Dunston"})
        self.assertIsNone(a)
        self.delete_test_db('deleteme')
    
    def test_query(self):
        create_database('deleteme', 'pets', self.initial_item)
        i = insert_item('deleteme', 'pets', self.other_item)
        j = insert_item('deleteme', 'pets', self.next_item)

        self.assertEqual(type(i), ObjectId)
        self.assertEqual(type(j), ObjectId)

        all_parrots = {'species': 'Parrot'}

        res = [_ for _ in query('deleteme', 'pets', all_parrots)]

        self.assertCountEqual(res, [self.other_item, self.next_item])

        self.delete_test_db('deleteme')
    
    def test_handle_code_change(self):
        create_database('deleteme', 'functions', self.function)
        #insert_item('deleteme', 'functions', self.function)
        latest = get_item(
            'deleteme',
            'functions', 
            {'name': 'dummyfunc'},
            **{'name': 1, 'type': 1, 'versions': {"$slice": -1}})
        new_docstring = {
            'name': 'dummyfunc',
            'versions': [
                {
                    'docstring': 'Returns Success',
                    'source': (
                        "def dummyfunc():\n"
                        "    return 1"
                    ),
                    'created': datetime.today().replace(microsecond=0)
                }
            ]
        }
        new_source = {
            'name': 'dummyfunc',
            'versions': [
                {
                    'docstring': 'Returns True always',
                    'source': (
                        "def dummyfunc():\n"
                        "    return 2"
                    ),
                    'created': datetime.today().replace(microsecond=0)
                }
            ]
        }
        #handle_code_change('functions', new_docstring, latest)
        #handle_code_change('functions', new_source, latest)
        #self.delete_test_db('deleteme')
        pass

    def test_get_version_field(self):
        pass

if __name__ == '__main__':
    unittest.main()
