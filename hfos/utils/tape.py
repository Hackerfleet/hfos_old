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

from hfos.database.mongoadaptors import MongoReader, MongoFindOne, MongoUpdateOne, MongoTail
from hfos.database.mongo import logbook
from hfos.database.migrations.initial import frames
from hfos.utils.logger import Logger, critical, log, info

import time

class TriggeredDataSource(component):
    def __init__(self, messages, loop):
        super(TriggeredDataSource, self).__init__()
        self.messages = messages
        self.counter = 0
        self.loop = loop

        log("[TDS] Playing back %i messages." % len(messages), lvl=info)


    def main(self):

        while len(self.messages) > 0 or self.loop:
            while not self.dataReady("inbox"):
                        self.pause()
                        yield 1

            self.recv("inbox")
            if self.loop:
                msg = self.messages[self.counter]
                self.counter += 1
                self.counter %= len(self.messages)
            else:
                msg = self.messages.pop(0)
            self.send(msg, "outbox")
            yield 1

        yield 1
        self.send(producerFinished(self), "signal")
        return

def build_tapeplayback(loop=False, delay=3):
    logbook.drop()
    playback = Pipeline(SimpleClock(delay),
        TriggeredDataSource(frames, loop=loop),
        Logger(name="TAPEPLAYBACK", level=info),
        PureTransformer(lambda x: dict({'time': time.time()}, **x)),
        MongoUpdateOne(logbook)
    ).activate()