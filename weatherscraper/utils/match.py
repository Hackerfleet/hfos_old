__author__ = 'riot'

from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess

from weatherscraper.logging import log

class Match(component):
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

    def __init__(self, matchfunction):
        super(Match, self).__init__()
        self.function = matchfunction

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


                if self.function(data):
                    self.send(data, "match")
                else:

                    self.send(data, "outbox")