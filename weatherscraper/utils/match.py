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
                log("[MATCHER] Data:", data)
                if self.function(data):
                    log("[MATCHER] MATCH!")
                    self.send(data, "match")
                else:
                    log("[MATCHER] Tried to match '%s' with '%s'" % (data, self.function))
                    self.send(data, "outbox")