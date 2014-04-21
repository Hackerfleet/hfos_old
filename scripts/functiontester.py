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

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Visualisation.Axon.AxonVisualiserServer import text_to_token_lists, AxonVisualiser

#from hfos.components import build_system

#from hfos.server.webui import build_WebU# I

from hfos.utils.selector import testPipeSelector

from hfos.database.mongoadaptors import MongoReader, MongoFindOne
from hfos.database.mongo import crew, groups
from hfos.utils.logger import Logger

def functiontest():
    tester = Pipeline(DataSource([0]),
                      MongoFindOne('uid', crew),
                      Logger(),
                      ConsoleEchoer()
    ).activate()

if __name__ == '__main__':
    #weatherScraper()
    #build_system(online=False, debug=True)
    #build_WebUI()
    functiontest()

    #Pipeline(Introspector(),
    #         text_to_token_lists(),
    #         AxonVisualiser(),
    #)#.activate()

    scheduler.run.runThreads()