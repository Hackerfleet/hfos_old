#! /usr/bin/env python3

__author__ = 'riot'

from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Clock import CheapAndCheerfulClock as SimpleClock
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Filter import Filter
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.File.WholeFileWriter import WholeFileWriter

from weatherscraper.utils.dict import DictTemplater
from weatherscraper.utils.templater import MakoTemplater
from weatherscraper.utils.httpgetter import HTTPGetter
from weatherscraper.filters.webfilter import Wetter24Filter, NasaSDOFilter


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
        DT=DictTemplater(templater=MakoTemplater('weather')),
        PT=PureTransformer(lambda x: ['/tmp/weather.html', x]),
        CE=ConsoleEchoer(),
        WFW=WholeFileWriter(),
        linkages={
            ("W24", "outbox"): ("DC", "inbox"),
            ("NSDOIMG", "outbox"): ("DC", "inbox"),
            ("BP", "outbox") : ("F", "inbox"),
            ("F", "outbox") : ("DT", "inbox"),
            ("DT", "outbox") : ("PT", "inbox"),
            ("PT", "outbox") : ("CE", "inbox")
        }
    )