__author__ = 'riot'

from Axon.Component import component
from Axon.AdaptiveCommsComponent import AdaptiveCommsComponent
from Axon.Ipc import producerFinished, shutdownMicroprocess

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

                if type(data) == dict and all(k in data for k in self.keys):
                    self.send(data, "outbox")
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
            if self.dataReady("inbox"):
                data = self.recv("inbox")
                if self.update:
                    self.values.update(data)
                else:
                    self.values = data

                self.send(self.templater.render(self.values), "outbox")

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
            while self.dataReady("inbox"):
                data = self.recv("inbox")

                if type(data) == dict:
                    #print("Input: '%s'" % data)
                    for key in self.keys:
                        if key in data:
                            self.send(data[key], key)

                    rest = {}
                    for key in data:
                        if key not in self.keys:
                            rest[key] = data[key]
                    self.send(rest, "outbox")
                else:
                    raise TypeError("I need dictionaries, not '%s'" % data)

            self.pause()
            yield 1
