__author__ = 'riot'

from Axon.ThreadedComponent import threadedcomponent
from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess
from pynmea.streamer import NMEAStream
import time

from weatherscraper.logging import log

import pygrib

class GribParser(threadedcomponent):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    Inboxes = { "inbox"   : "Items",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Items tagged with a sequence number, in the form (seqnum, item)",
                 "signal" : "Shutdown signalling",
               }

    def __init__(self, gribfile=""):
        super(GribParser, self).__init__()
        self.gribfile = gribfile


    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) == shutdownMicroprocess:
                self.send(msg, "signal")
                return True
        return False

    def main(self):
        """Main loop."""

        self.gribdata = pygrib.open(self.gribfile)

        while not self.finished():
            while not self.anyReady():
                time.sleep(0.1)

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                lat, lon = data

                result = []

                log("Parsing grib for coords '%f:%f" % (lat, lon))

                for no, grb in enumerate(self.gribdata):
                    glat, glon = grb.latlons()

                    if (glat.min() < lat) and (glat.max() > lat) and (glon.min() < lon) and (glon.max() > lon):
                        dimension = ((glat.min(), glon.min()),(glat.max(), glon.max()))
                        result.append(str((no, dimension, (grb))) + "\n")  # yuck, ECMWF starts counting at 1


                self.send(result, "outbox")