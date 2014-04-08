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

import serial
from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished, shutdownMicroprocess

from hfos.utils.logger import log

class SerialReader(threadedcomponent):
    """SerialReader, either listening, writing or even both!"""

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
        super(SerialReader, self).__init__()
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