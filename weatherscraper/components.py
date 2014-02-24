#! /usr/bin/env python3

__author__ = 'riot'

import time

from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Util.Clock import SimpleClock
from Kamaelia.Util.Filter import Filter
from Kamaelia.File.WholeFileWriter import WholeFileWriter
from Kamaelia.File.Reading import SimpleReader
from Kamaelia.Util.Stringify import Stringify
from Kamaelia.Util.Collate import Collate
from Kamaelia.Util.DataSource import TriggeredSource, DataSource
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Util.Console import ConsoleEchoer

from weatherscraper.utils.dict import DictTemplater
from weatherscraper.utils.templater import MakoTemplater
from weatherscraper.utils.httpgetter import HTTPGetter
from weatherscraper.filters.webfilter import Wetter24Filter, NasaSDOFilter


def siteScraper(url, interval, filterclass):
    """Constructs a sitescraper containing a SimpleClock, TriggeredSource, HTTPGetter and Filter"""

    return Pipeline(SimpleClock(interval),
                    TriggeredSource(url),
                    HTTPGetter(decode=True),
                    Filter(filterclass)
                    )


def siteDebugger(filename, interval, filterclass):
    """Replacement function to not bother webpages you already downloaded
    for debugging purposes.
    Just replace
        siteScraper(url, ...
    with
        siteDebugger(path-to-dumped-file, ...
    (Leave the rest intact, less work and the filter is still required!)
    """

    return Pipeline(
        SimpleReader(filename),
        Collate(),
        Stringify(),
        Filter(filterclass)
    )


def fileDownloader(url, target, interval):
    """Constructs a filedownloader containing a SimpleClock, HTTPGetter and SimpleFileWriter"""

    return Pipeline(SimpleClock(interval),
                    TriggeredSource(url),
                    HTTPGetter(),
                    PureTransformer(function=lambda x: [target, x]),
                    WholeFileWriter()
                    )


def weatherSaver():
    """Stores the weather web pages for local debugging purposes
    """
    from Kamaelia.File.Writing import SimpleFileWriter

    Pipeline(
        DataSource(["http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html"]),
        HTTPGetter(),
        SimpleFileWriter('/tmp/w24.html', mode="wb")
    ).run()
    Pipeline(
        DataSource(["http://sdo.gsfc.nasa.gov/data/"]),
        HTTPGetter(),
        SimpleFileWriter('/tmp/sdo.html', mode="wb")
    ).run()


def addtime(x):
    """Helper function to insert a timestamp into a dictionary
    """
    x.update({'year': time.gmtime()[0],
              'month': time.gmtime()[1],
              'day': time.gmtime()[2],
              'hour': time.gmtime()[3],
              'minute': time.gmtime()[4],
              'seconds': time.gmtime()[5]})
    return x


def weatherScraper(location='/tmp/test', interval=600):
    """Constructs a weathersite scraper, in ijon's c-beam style"""

    rainradar = Pipeline(
        SimpleClock(interval),
        TriggeredSource("http://wind.met.fu-berlin.de/loops/radar_100/R.NEW.gif"),
        HTTPGetter(),
        PureTransformer(function=lambda x: [location + "/rainradar.gif", x]),
    ).activate()

    nasa_sdo = Pipeline(
        siteScraper("http://sdo.gsfc.nasa.gov/data/",
                    interval=interval,
                    filterclass=NasaSDOFilter()
                    ),
        HTTPGetter(),
        PureTransformer(function=lambda x: [location + "/nasa_sdo.jpg", x]),
    ).activate()

    w24 = Pipeline(
        siteScraper("http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html",
                    interval=interval,
                    filterclass=Wetter24Filter()
                    ),
        PureTransformer(function=addtime),
        DictTemplater(templater=MakoTemplater('weather')),
        PureTransformer(function=lambda x: [location + "/weather.html", x]),
    ).activate()

    Graphline(RR=rainradar,
                       NSDO=nasa_sdo,
                       W24=w24,
                       WFW=WholeFileWriter(),
                       CE=ConsoleEchoer(),
                       linkages= {
                           ("RR", "outbox") : ("WFW", "inbox"),
                           ("NSDO", "outbox") : ("WFW", "inbox"),
                           ("W24", "outbox"): ("WFW", "inbox")
                       }
    ).activate()