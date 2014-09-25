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

import voluptuous
from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.Console import ConsoleEchoer

from hfos.utils.logger import log, debug, error


class Validator(component):
    """
    Validates input data using voluptuous

    Input data is either sent out to
    * valid - when the given schema valid
    * invalid - when it does not

    """

    Inboxes = {"inbox": "Items",
               "control": "Shutdown signalling",
    }
    Outboxes = {"valid": "Items that have been valid successfully",
                "invalid": "All the rest",
                "signal": "Shutdown signalling",
    }

    def __init__(self, schema, exception=voluptuous.Invalid):
        super(Validator, self).__init__()
        self.schema = schema

        # TODO: Is dynamic exception handling useful here at all?
        self.exception = exception


    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (shutdownMicroprocess, producerFinished):
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

            log("[V] data: ", data, "type:", type(data), lvl=debug)

            valid_data = None

            try:
                valid_data = self.schema(data)
                log("[V] Valid data received: ", valid_data, lvl=debug)
            except self.exception as ve:
                log("[V] Validation error:", ve, data, lvl=error)  # TODO: This level and msg a good idea?

            if valid_data:
                self.send(data, "valid")
            else:
                self.send(data, "invalid")


def testValidator():
    """
    Testing is WiP.
    This one works by staring at its log output - pretty bad for a validator, huh?
    I think a testing component might be in order.
    """

    from hfos.utils.validator import Validator
    from Kamaelia.Util.PureTransformer import PureTransformer
    from voluptuous import Schema, Required


    def do_test(schema, data):
        tester = Graphline(DS=DataSource([data]),
                           V=Validator(schema),
                           PTIV=PureTransformer(lambda x: ('invalid', x)),
                           PTV=PureTransformer(lambda x: ('valid', x)),
                           CE=ConsoleEchoer(),
                           linkages={
                               ('DS', 'outbox'): ('V', 'inbox'),
                               ('V', 'valid'): ('PTV', 'inbox'),
                               ('V', 'invalid'): ('PTIV', 'inbox'),
                               ('PTV', 'outbox'): ('CE', 'inbox'),
                               ('PTIV', 'outbox'): ('CE', 'inbox')
                           }
        ).activate()

    schema = Schema({Required('request'): str})

    do_test(schema, {'request': 'foobar'})
    do_test(schema, {'fail': 'foobar'})
    do_test(schema, {'request': 123})
