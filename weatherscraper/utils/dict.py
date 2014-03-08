#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__author__ = 'riot'

from Axon.Component import component
from Axon.AdaptiveCommsComponent import AdaptiveCommsComponent
from Axon.Ipc import producerFinished, shutdownMicroprocess

from weatherscraper.logging import log

class TupleToDict(component):
    """
    Converts incoming tuples into dictionaries according
    to a given key.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, keys):
        super(TupleToDict, self).__init__()
        self.keys = []

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
            data = self.recv("inbox")

            assert (len(data) == len(self.keys))

            result = {}
            for i, key in enumerate(self.keys):
                result[key] = data[i]
            self.send(result, "outbox")


class DictCollator(component):
    """
    Collects incoming key/value pairs or dicts and
    merges them upon producerFinished
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self):
        super(DictCollator, self).__init__()
        self.collation = {}

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
            data = self.recv("inbox")
            log("Whoa:", data)

            if type(data) == dict:
                self.collation.update(data)
            elif type(data) in ([], ()):
                self.collation.update({data[0]: data[1]})
            self.send(self.collation, "outbox")

class WaitForDict(component):
    """
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, keys):
        super(WaitForDict, self).__init__()
        self.keys = keys
        self.data = {}

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
            if self.dataReady("inbox"):
                data = self.recv("inbox")
                #log("[WFD]: data:", str(data)[:23])

                if type(data) == dict:
                    self.data.update(data)
                    if all(k in self.data for k in self.keys):
                        #log("[WFD] Yup, transmitting.")
                        self.send(self.data, "outbox")
                        self.data = {}
                else:
                    pass
                    #log("[WFD] nope: ", self.keys, data.keys())
            self.pause()
            yield 1



class DictTemplater(AdaptiveCommsComponent):
    """
    """


    def __init__(self, templater, update=True):
        super(DictTemplater, self).__init__()
        self.templater = templater
        self.update = update
        self.values = {}

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
                yield 1

            if self.dataReady("control"):
                log("[DT]: control message:", self.recv("control"))

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                log("[DT] Incoming: ", data)
                if self.update:
                    self.values.update(data)
                else:
                    self.values = data

                self.send(self.templater.render(self.values), "outbox")

            self.pause()
            yield 1





class ToNamedDict(AdaptiveCommsComponent):
    """Converts the input into a dictionary, then sends on.
    """

    # TODO: Is this component really necessary?!

    def __init__(self, keys):
        super(ToNamedDict, self).__init__()
        self.keys = keys
        self.namedDict = {}
        for key in keys:
            name = self.addInbox(key)
            if name != key:
                log("[TND]: Can't assign boxname '%s' != '%s'" % (key, name))

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
                yield 1

            for key in self.keys:
                if self.dataReady(key):
                    log("[TND]: Received key '%s'" % key)
                    self.namedDict[key] = self.recv(key)

            if set(self.namedDict.keys()) == set(self.keys):
                log("[TND]: Received all keys. Punching out '%s'." % self.namedDict.keys())
                self.send(self.namedDict, "outbox")
                self.namedDict = {}
            else:
                log("[TND]: I have '%s' - i need '%s'" % (self.namedDict.keys(), self.keys))

            self.pause()
            yield 1




class ToDict(component):
    """Converts the input into a dictionary, then sends on.
    """

    # TODO: Is this component really necessary?!

    def __init__(self):
        super(ToDict, self).__init__()

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
            while self.dataReady("inbox"):
                data = self.recv("inbox")
                try:
                    self.send(data.__dict__, "outbox")
                except:
                    raise TypeError("Unexpected non-dictionary '%s'" % data)
            self.pause()
            yield 1


class DictPicker(component):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, keyname):
        super(DictPicker, self).__init__()
        self.keyname = keyname

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
            while self.dataReady("inbox"):
                data = self.recv("inbox")

                if type(data) == dict:
                    self.send(data[self.keyname], "outbox")

            self.pause()
            yield 1


class DictSplitter(AdaptiveCommsComponent):
    """Splits a dictionaries' values into several outboxes by given keys.
    The rest is sent on via outbox.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, keys):
        super(DictSplitter, self).__init__()
        self.keys = keys
        for key in keys:
            name = self.addOutbox(key)
            if name != key:
                raise ValueError("Cannot create outbox for key '%s' (boxname would be '%s')." % (key, name))

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

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                log("[DS] Incoming: ", data)
                if type(data) == dict:
                    log("[DS] Input: '%s'" % data)
                    for key in data.keys():
                        if key in self.keys:
                            log("[DS] Sending '%s' to %s" % (data[key], key))
                            self.send(data[key], key)
                        else:
                            log("[DS] Don't know where to send {%s:%s}" % (key, data[key]))
                            log(self.outboxes)

                    rest = {}
                    for key in data:
                        if key not in self.keys:
                            rest[key] = data[key]
                    self.send(rest, "outbox")
                else:
                    raise TypeError("I need dictionaries, not '%s'" % data)

            self.pause()
            yield 1
