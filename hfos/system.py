#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

from hfos.components import build_nmeaSubscribers
from hfos.components import build_nmeaPublisher
from hfos.server.webui import build_webui


def build_system(online=True, debug=True):
    #build_nmeaSubscribers()
    #build_nmeaPublisher(debug)
    build_webui()

    #if online:
    #    build_weatherScraper()
