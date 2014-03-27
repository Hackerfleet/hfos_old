#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from Axon.Component import component
from Axon.AdaptiveCommsComponent import AdaptiveCommsComponent
from Axon.Ipc import producerFinished, shutdownMicroprocess
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.Console import ConsoleEchoer

from hfos.logging import log, debug, warn

from pymongo import MongoClient
from pymongo.collection import Collection

host = 'localhost'
port = 27017
dbname = 'hfos'

mongoclient = MongoClient(host, port)
mongodb = mongoclient[dbname]


class MongoFindOne(component):
    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, key, collection):
        super(MongoFindOne, self).__init__()
        self.key = key

        assert (type(collection) == Collection)
        self.collection = collection


    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def main(self):
        """Main loop."""

        while not self.finished():
            while not self.dataReady("inbox"):
                self.pause()
                yield 1
            value = self.recv("inbox")

            result = self.collection.find_one({self.key: value})
            log("FOO\n", value, "BAR\n", result)
            self.send(result, "outbox")
            yield 1



class MongoReader(component):
    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self):
        super(MongoReader, self).__init__()

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def main(self):
        """Main loop."""

        while not self.finished():
            while not self.dataReady("inbox"):
                self.pause()
                yield 1
            col = self.recv("inbox")

            assert (type(col) == Collection)

            for result in col.find():
                self.send(result, "outbox")
                yield 1
