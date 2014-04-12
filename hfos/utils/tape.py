#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from Axon.Component import component
from Axon.Ipc import producerFinished
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Util.TwoWaySplitter import TwoWaySplitter
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Collate import Collate
from Kamaelia.Util.Clock import SimpleClock

from hfos.database.mongo import MongoReader, MongoFindOne, MongoUpdateOne, MongoTail
from hfos.database.migration import logbook
from hfos.database.migrations.initial import frames
from hfos.utils.logger import Logger, critical, log, info

class TriggeredDataSource(component):
    def __init__(self, messages):
        super(TriggeredDataSource, self).__init__()
        self.messages = messages
        log(messages)
        log(len(messages))

    def main(self):

        while len(self.messages) > 0:
            while not self.dataReady("inbox"):
                        self.pause()
                        yield 1

            self.recv("inbox")
            self.send(self.messages.pop(0), "outbox")
            yield 1

        yield 1
        self.send(producerFinished(self), "signal")
        return

def build_tapeplayback():
    logbook.drop()
    playback = Pipeline(SimpleClock(3),
                        Logger(name="TAPEPLAYBACK", level=info),
        TriggeredDataSource(frames),
        MongoUpdateOne(logbook)
    ).activate()