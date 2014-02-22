#! /usr/bin/env python3

__author__ = 'riot'

from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Clock import CheapAndCheerfulClock as SimpleClock
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Filter import Filter

from weatherscraper.utils.httpgetter import HTTPGetter
from weatherscraper.filters import Wetter24Filter, NasaSDOFilter


def siteScraper(url, interval, filter):
    """Constructs a sitescraper containing a SimpleClock, HTTPGetter and Filter"""

    return Pipeline(SimpleClock(interval),
                    HTTPGetter(url),
                    Filter(filter)
    )


def weatherScraper():
    """Constructs a weathersite scraper"""

    return Graphline(
        W24=siteScraper("http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html",
                        interval=15,
                        filter=Wetter24Filter()
        ),
        NSDOIMG=siteScraper("http://sdo.gsfc.nasa.gov/data/",
                            interval=23,
                            filter=NasaSDOFilter()
        ),

        CE=ConsoleEchoer(),
        linkages={
            ("W24", "outbox"): ("CE", "inbox"),
            ("NSDOIMG", "outbox"): ("CE", "inbox")
        }
    )
