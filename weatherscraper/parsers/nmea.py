__author__ = 'riot'

from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess
from pynmea.streamer import NMEAStream
import time

from weatherscraper.logging import log


class NMEAParser(component):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self):
        super(NMEAParser, self).__init__()
        self.streamer = NMEAStream()
        #self.streamer.get_objects("\n")

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def _parse(self, data):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and returned as NMEASentence object
        """
        sentences = []
        sen_time = time.time()  # TODO: This is late due to message traversal etc.

        # TODO: Something here is fishy, as in the first received packet
        # gets lost in the NMEAStream object. WTF.

        for sentence in self.streamer.get_objects(data, size=len(data)+1):
            nmeadata = sentence.__dict__
            del(nmeadata['parse_map'])
            del(nmeadata['nmea_sentence'])
            nmeadata['time'] = sen_time
            nmeadata['type'] = sentence.sen_type
            #sentences.append(nmeadata)
            self.send(nmeadata, "outbox")

        #return sentences

    def main(self):
        """Main loop."""

        while not self.finished():
            while not self.anyReady():
                self.pause()
                yield 1

            while self.dataReady("inbox"):
                data = self.recv("inbox")

                if len(data) > 0:
                    if data[-1] != "\n":
                        data += "\n"
                    self._parse(data)
#
#                    if result:
#                        for sentence in result:
#                            self.send(sentence, "outbox")
                yield 1

