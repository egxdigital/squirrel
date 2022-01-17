"""Queries

This module contains MongoDB queries for the Squirrel program.

Examples
    python -m unittest tests.test_queries
"""
import sys
from pprint import pprint
from typing import List
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import ReturnDocument

from squirrel.helpers import *


def has_database(db_name: str) -> bool:
    if has_client():
        return db_name in MongoClient().list_database_names()
    return False


def has_client(client_uri: str = None) -> bool:
    timeout = 500
    try:
        running_client = MongoClient(
            client_uri, serverSelectionTimeoutMS=timeout)
    except ServerSelectionTimeoutError as e:
        print("no running mongo instance detected!")
        print("run 'service mongod status'")
        return False
    else:
        ver = running_client.server_info().get('version')
        #print(f"MongoDB version {ver} available!")
        return True


def create_database(db_name: str, collection: str, *initial: dict) -> Database:
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
    else:
        try:
            col.insert_many(initial)
        except Exception as e:
            print(e)
            return None
        else:
            return db


def insert_item(db_name: str, collection: str, item: dict, **kwargs) -> ObjectId:
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        try:
            x = col.insert_one(item, kwargs)
        except Exception as e:
            print(e)
            return None
        else:
            return x.inserted_id


def insert_many_items(db_name: str, collection: str, *items):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        try:
            ins = col.insert_many(items)
        except Exception as e:
            print(e)
            return None
        else:
            return ins.inserted_ids


def insert_unique_item(db_name: str, collection: str, query: dict):
    if item_exists(db_name, collection, query):
        return None
    return insert_item(db_name, collection, query)


def item_exists(db_name: str, collection: str, query: dict) -> bool:
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return False
    else:
        return col.find_one(query) != None


def get_item(db_name: str, collection: str, it: dict, **kwargs):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        return col.find_one(it, kwargs)


def get_many_items(db_name: str, collection: str, **kwargs):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        return col.find({}, kwargs)


def get_all_items_in_collection(db_name: str, collection: str) -> List:
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
        cursor = col.find({})
    except Exception as e:
        print(e)
        return None
    else:
        result = []
        for docu in cursor:
            #pprint(docu)
            result += [docu]
        
        return result


def update_item(db_name: str, collection: str, to_update: dict, changes: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        new_values = {"$set": changes}
        return col.update_one(to_update, new_values)


def update_many(db_name: str, collection: str, query: dict, changes: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        new_values = {"$set": changes}
        return col.update_many(query, new_values)


def insert_embedded_document(db_name: str, collection: str, query: dict, new_item: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        new_values = {"$push": new_item}
        return col.update_one(query, new_values)


def find_one_and_update(db_name: str, collection: str, fil: dict, update: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        try:
            new_values = {"$set": update}
            it = col.update(
                fil,
                new_values
            )
        except Exception as e:
            print(e)
            return None
        else:
            return it


def add_field(db_name: str, collection: str, it: dict, new_value: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        new_values = {"$inc": new_value}
        return col.update_one(it, new_values)


def remove_one(db_name: str, collection: str, item: dict, **kwargs):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        try:
            x = col.delete_one(item, kwargs)
        except Exception as e:
            print(e)
            return None
        else:
            return x


def remove_many(db_name: str, collection: str, fil: dict, **kwargs):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        try:
            x = col.delete_many(fil, kwargs)
        except Exception as e:
            print(e)
            return None
        else:
            return x


def query(db_name: str, collection: str, query: dict):
    try:
        client = MongoClient()
        db = client[db_name]
        col = db[collection]
    except Exception as e:
        print(e)
        return None
    else:
        return col.find(query)


def handle_code_change(db_name, col: str, incoming: dict, existing: dict, named: str) -> dict:
    """
    Updates the document for a specified code object. 
    A named update results in a new version. An unnamed 
    update results in an update to the selected version 
    or the latest version by default.

    Parameters
    ----------
    col : str
        [description]
    incoming : dict
        [description]
    latest : dict
        [description]

    Returns
    -------
    dict
        [description]
    """
    name               = existing['name']
    incoming_version   = incoming['versions'][-1]
    incoming_docstring = incoming_version['docstring']
    incoming_source    = incoming_version['source']

    ver_names = [ver['version_name'] for ver in existing['versions']]
    
    if named not in ver_names:
        insert_embedded_document(
            db_name=db_name,
            collection=col,
            query={"name": name},
            new_item={"versions": incoming_version}
        )
        return
    
    for version in existing['versions']:
        version_name         = version['version_name']
        existing_docstring   = version['docstring']
        existing_source      = version['source']
        if incoming_docstring != existing_docstring:
            update_item(
                db_name,
                col,
                {
                    "name": name,
                    "versions.version_name": named
                },
                {"versions.$.docstring": incoming_docstring}
            )
        if incoming_source != existing_source:
            update_item(
                db_name,
                col,
                {
                    "name": name,
                    "versions.version_name": named
                },
                {"versions.$.source": incoming_source}
            )


def get_version_field(db: str, field: str, citizen: str, name: str, version: str):
    document = get_item(
        db,
        COLLECTIONS[citizen], 
        {"name": name}, 
        **{'name': 1, 'type': 1, 'versions': 1}
        )
    for ver in document['versions']:
        if ver['version_name'] == version:
            result = ver[field]
            return result





