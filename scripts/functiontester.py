__author__ = 'riot'

from Axon.Scheduler import scheduler

from weatherscraper.utils.serialreader import Serialport
from weatherscraper.utils.dict import DictPicker, DictSplitter, DictTemplater
from weatherscraper.filters.nmeafilter import nmeaFilter
from weatherscraper.parsers.nmea import NMEAParser
from weatherscraper.utils.templater import MakoTemplater


from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Util.TagWithSequenceNumber import TagWithSequenceNumber

from Kamaelia.Util.Clock import SimpleClock

from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.DataSource import DataSource, TriggeredSource
from Kamaelia.Util.Filter import Filter
from Kamaelia.Util.PureTransformer import PureTransformer

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo

from weatherscraper.components import weatherSaver, weatherScraper, gribGetter, gribAnalyzer

def test_nmeaPublisher():

    nmeaPublisher = Pipeline(DataSource(["$GPALM,32,1,01,5,00,264A,4E,0A5E,FD3F,A11257,B8E036,536C67,2532C1,069,000*7B",
                                        "$GPALM,32,1,01,5,00,264A,4E,0A5E,FD3F,A11257,B8E036,536C67,2532C1,069,000*7B",
                                        "$GPRMC,162614,A,5230.5900,N,01322.3900,E,10.0,90.0,131006,1.2,E,A*13",
                                        "$GPALM,32,1,01,5,00,264A,4E,0A5E,FD3F,A11257,B8E036,536C67,2532C1,069,000*7B",
                                        "$GPRMC,162614,A,5230.5900,N,01322.3900,E,10.0,90.0,131006,1.2,E,A*13",
                                        "$GPALM,32,1,01,5,00,264A,4E,0A5E,FD3F,A11257,B8E036,536C67,2532C1,069,000*7B",
                                        "$GPRMC,162614,A,5230.5900,N,01322.3900,E,10.0,90.0,131006,1.2,E,A*13",

                                        ""]),
                            #Serialport('/dev/ttyUSB0'),
                            NMEAParser(),
                            PublishTo("NMEA")
    ).activate()

    navtemplate = """
    Current heading: {true_course}\n
    Current speed: {spd_over_grnd}
    """

    navDataGetter = Graphline(BP=SubscribeTo("NMEA"),
                              F=Filter(filter=nmeaFilter("GPRMC")),
                              DT=DictTemplater(templater=MakoTemplater('navdisplay')),
                              PT=PureTransformer(lambda x: ("navdisplay", x)),
                              CE=ConsoleEchoer(),
                              linkages={
                                  ("BP", "outbox") : ("F", "inbox"),
                                  ("F", "outbox") : ("DT", "inbox"),
                                  ("DT", "outbox") : ("PT", "inbox"),
                                  ("PT", "outbox") : ("CE", "inbox")
                              }
                              ).activate()

    trueCourseFinder = Pipeline(SubscribeTo("NMEA"),
                               Filter(filter=nmeaFilter("GPRMC")),
                               DictPicker('true_course'),
                               ConsoleEchoer()
    )#.activate()

    trueSpeedFinder = Pipeline(SubscribeTo("NMEA"),
                               Filter(filter=nmeaFilter("GPRMC")),
                               DictPicker('spd_over_grnd'),
                               ConsoleEchoer()
    )#.activate()

    nmeaAlmConsumer = Pipeline(SubscribeTo("NMEA"),
                               Filter(filter=nmeaFilter("GPALM")),
                               ConsoleEchoer()
    )#.activate()

    Backplane("NMEA").run()

if __name__ == '__main__':
    gribAnalyzer()
    scheduler.run.runThreads()