#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

host = 'localhost'
port = 27017

from pymongo import MongoClient, collection

client = MongoClient(host, port)
db = client['hfos']
crew = db['crew']
sensordata = db['sensordata']
groups = db['groups']
logbook = db['logbook']

def update(collection, query, object):
    existing = collection.find_one(query)
    col_name = collection.full_name
    obj_id = "FAIL"
    if existing:
        if existing.keys() == object.keys():
            print("%s: Not updating: " % col_name, end="")
            obj_id = existing["_id"]
        else:
            print("%s: Updated object: " % col_name, end="")
            obj_id = collection.insert(object)
    else:
        print("%s: Inserting object: " % col_name, end="")
        obj_id = collection.insert(object)

    print(obj_id)
    return obj_id

