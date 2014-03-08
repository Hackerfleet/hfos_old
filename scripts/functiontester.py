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
from Kamaelia.Visualisation.Axon.AxonVisualiserServer import text_to_token_lists, AxonVisualiser

from weatherscraper.components import build_system

from weatherscraper.server.webui import build_WebUI

from weatherscraper.utils.selector import testPipeSelector

if __name__ == '__main__':
    #weatherScraper()
    #build_system(online=False, debug=True)
    build_WebUI()

    #Pipeline(Introspector(),
    #         text_to_token_lists(),
    #         AxonVisualiser(),
    #)#.activate()

    scheduler.run.runThreads()