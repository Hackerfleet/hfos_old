__author__ = 'riot'

import serial

from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished, shutdownMicroprocess

from weatherscraper.logging import log

class Serialport(threadedcomponent):
    """Serialport, either listening, writing or even both!"""

    Inboxes = {
        "inbox": "When signalled, downloads the configured url and sends it to the outbox. ",
        "control": ""
    }
    Outboxes = {
        "outbox": "Sends out the retrieved raw data",
        "debug": "Debug output",
        "signal": ""
    }

    def __init__(self, device, mode="r", speed=9600, bytesize=8, parity='N', stopbits=1, autoconnect=True,
                 xonxoff=0, buffersize=100):
        super(Serialport, self).__init__()
        self.device = device
        self.mode = mode
        self.speed = speed
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = None  # Hmmm.
        self.xonxoff = xonxoff
        self.buffersize = buffersize
        self.readline = True

        self.listening = True
        self.buf = ""
        self.port = None

        if autoconnect:
            log("Connecting serialport '%s'" % device)
            self._connect()


    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def main(self):
        while not self.finished():
            if self.port and self.port.isOpen() and self.listening:
                self.buf = self.buf + str(self.port.read(self.port.inWaiting()))

                if self.readline:
                    if '\n' in self.buf:
                        lines = self.buf.split('\n')  # Guaranteed to have at least 2 entries
                        line = lines[-2]
                        self.buf = lines[-1]

                        self.send(line, "outbox")
                else:
                    self.send(self.buf, "outbox")
                    self.buf = ""

    def _connect(self):

        if self.port and self.port.isOpen():
            return False
        try:
            self.port = serial.Serial(port=self.device,
                                      baudrate=self.speed,
                                      parity=self.parity,
                                      stopbits=self.stopbits,
                                      bytesize=self.bytesize,
                                      )
                                      
            self.port.flush()
            ("YAY!")
            return True
        
        except Exception as error:

            log("Failed to open device: %s" % error)
            self.port = None
            return False

    def _disconnect(self, flush=False):
        if isinstance(self.port, serial.Serial):
            if self.port.isOpen() and flush:
                # This may need exception catching
                self.port.flush()
            self.port.close()
            return True
        else:
            return False

    def _write(self, args):
        """Don't even look at me."""
        if not "w" in self.mode or not self.port:
            return False

        try:
            if len(args) > 0:
                for byte in args:
                    self.port.write(byte)
                if self.readline and args[-1] != "\n":
                    self.port.write("\n")
            elif self.readline:
                self.port.write("\n")
            return True
        except Exception as error:
            log("Failed to write: %s" % error)
            return False