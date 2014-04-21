#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

host = 'localhost'
port = 27017

from hfos.utils.logger import log

from pymongo import MongoClient, collection

client = MongoClient(host, port)
db = client['hfos']
switches = db['switches']
gauges = db['gauges']
crew = db['crew']
sensordata = db['sensordata']
groups = db['groups']
logbook = db['logbook']

def insert(collection, object):
    obj_id = collection.insert(object)  # Hmhmho. How useful.
    log("%s: Inserted object: " % collection.full_name, obj_id)
    return obj_id

def update(collection, query, object):
    existing = collection.find_one(query)
    col_name = collection.full_name
    obj_id = "FAIL"
    if existing:
        if existing.keys() == object.keys():
            obj_id = existing["_id"]
            log("%s: Not updated: " % col_name, obj_id)
        else:
            obj_id = collection.insert(object)
            log("%s: Updated object: " % col_name, obj_id)
    else:
        obj_id = collection.insert(object)
        log("%s: Inserted object: " % col_name, obj_id)

    return obj_id

