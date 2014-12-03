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


import time
import sys

from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess
import inspect

debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

lvldata = {10: ['DEBUG', '\033[1;97m'],
           20: ['INFO', '\033[1;92m'],
           30: ['WARN', '\033[1;94m'],
           40: ['ERROR', '\033[1;91m'],
           50: ['CRITICAL', '\033[1;95m'],
}

count = 0

logfile = "/var/log/hfos/service.log"
verbosity = {'global': info,
             'file': off,
             'console': debug}

start = time.time()


def log(*what, **kwargs):
    if 'lvl' in kwargs:
        lvl = kwargs['lvl']
        if lvl < verbosity['global']:
            return
    else:
        lvl = info

    global count
    global start
    count += 1

    now = time.time() - start
    msg = "[%s] : %8s : %.5f : %i :" % (time.asctime(),
                                         lvldata[lvl][0],
                                         now,
                                         count)
    if verbosity['global'] <= debug:
        "Automatically log the current function details."

        # Get the previous frame in the stack, otherwise it would
        # be this function!!!
        func = inspect.currentframe().f_back.f_code
        # Dump the message + the name of this function to the log.
        callee = "[%.10s@%s:%i]" % (
            func.co_name,
            func.co_filename,
            func.co_firstlineno
        )
        msg += "%-60s" % callee

    for thing in what:
        msg += " "
        msg += str(thing)

    if lvl >= verbosity['file']:
        try:
            f = open(logfile, "a")
            f.write(msg)
            f.flush()
            f.close()
        except IOError:
            print("Can't open logfile for writing!")
            sys.exit(23)

    if lvl >= verbosity['console']:
        print(lvldata[lvl][1], str(msg), '\033[0m')


class Logger(component):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    Inboxes = {"inbox": "Items",
               "control": "Shutdown signalling",
    }
    Outboxes = {"outbox": "Items not matching are sent along",
                "match": "All matches are sent this way",
                "signal": "Shutdown signalling",
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
                # print("#"*55)
                log("[%s] %s" % (self.name, str(data)), lvl=self.level)
                self.send(data, "outbox")
