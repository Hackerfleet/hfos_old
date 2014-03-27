#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"


from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess

from hfos.logging import log

debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

class Logger(component):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items not matching are sent along",
                 "match"  : "All matches are sent this way",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, level=debug, name="UNNAMED"):
        super(Logger, self).__init__()
        self.level = level
        self.name = name

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
            while not self.anyReady():
                self.pause()
                yield 1

            while self.dataReady("inbox"):
                data = self.recv("inbox")
                print("#"*55)
                log("[%s] %s" % (self.name, str(data)), lvl=self.level)
                self.send(data, "outbox")