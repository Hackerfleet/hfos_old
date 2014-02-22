#! /usr/bin/python

__author__ = 'riot'

import time
import urllib.request
import urllib.error
import socket


from Axon.Ipc import producerFinished, shutdownMicroprocess
from Axon.ThreadedComponent import threadedcomponent
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Clock import CheapAndCheerfulClock as SimpleClock
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Filter import Filter


class HTTPGetter(threadedcomponent):
    Inboxes = {
        "inbox": "When signalled, downloads the configured url and sends it to the outbox. ",
        "control": ""
    }
    Outboxes = {
        "outbox": "Sends out the retrieved raw data",
        "debug": "Debug output",
        "signal": ""
    }

    def __init__(self, url, proxy=False, useragent=False, timeout=30, postdata=None, extraheaders=None, realm=False,
                 username=False, password=False, decode=True):
        super(HTTPGetter, self).__init__()
        self.url = url
        self.proxy = proxy
        self.useragent = useragent
        self.timeout = timeout
        self.postdata = postdata
        self.decode = decode

        # Configure proxy
        if proxy:
            proxyhandler = urllib.request.ProxyHandler({"http": self.proxy})
        else:
            proxyhandler = None

        # Configure authentication
        if username and password:
            authhandler = urllib.request.HTTPBasicAuthHandler()

            authhandler.add_password(realm=realm,
                                     uri=url,
                                     user=username,
                                     passwd=password)

            # Generate opener

            if proxy:
                urlopener = urllib.request.build_opener(authhandler, proxyhandler)
            else:
                urlopener = urllib.request.build_opener(authhandler)
        elif proxy:
            urlopener = urllib.request.build_opener(proxyhandler)
        else:
            urlopener = urllib.request.build_opener()

        # Get ready to grab data
        urllib.request.install_opener(urlopener)
        if self.useragent:
            headers = {'User-Agent': self.useragent}
        else:
            headers = dict()

        if extraheaders:
            headers.update(extraheaders)

        self._req = urllib.request.Request(url=url, headers=headers)

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if isinstance(msg, producerFinished) or isinstance(msg, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def geturldata(self):
        """Gets the configured webpage and transmits it via outbox.
        """

        content = ""
        connection = None

        # Open connection
        try:
            connection = urllib.request.urlopen(self._req, timeout=self.timeout)
        except (urllib.error.ContentTooShortError,
                urllib.error.HTTPError,
                urllib.error.URLError,
                socket.timeout,
                UnicodeEncodeError,
                UnicodeDecodeError) as e:
            self.send([type(e), e], "debug")

        # Read and return requested content
        if connection:
            try:
                content = connection.read()
            except (socket.timeout, socket.error) as e:
                self.send([type(e), e], "debug")

            connection.close()

        if self.decode:
            content = str(content)

        return content

    def main(self):
        """Await input signal, then run our job, as long as we're not finished.
        """

        while not self.finished():
            if self.dataReady("inbox"):
                self.recv("inbox")
                # Data format: True
                urldata = self.geturldata()
                # Data format: [OK/Error,message]
                self.send(urldata, "outbox")

            time.sleep(0.1)


class Wetter24Filter(object):
    """Filters out interesting info from wetter24.de"""

    # TODO: Make sure, unicode is handled correctly
    # TODO: Strip of unnecessary data

    def filter(self, newtext):
        local_weather = newtext[newtext.find('head_ww'):newtext.find('hPa<') + 4]

        condition_zahl = local_weather.find('head_ww')
        condition_begin = local_weather.find('alt="', condition_zahl) + 5
        condition_end = local_weather.find('"', condition_begin)
        condition = local_weather[condition_begin:condition_end]

        temp_zahl = local_weather.find('head_tt2')
        temp_begin = local_weather.find('>', temp_zahl) + 1
        temp_end = local_weather.find('</p>', temp_zahl)
        temp = local_weather[temp_begin:temp_end]

        wind_zahl = local_weather.find('wind32px')
        wind_begin = local_weather.find('alt="', wind_zahl) + 5
        wind_end = local_weather.find('" title', wind_zahl)
        wind = local_weather[wind_begin:wind_end]

        w_speed_zahl = local_weather.find('head_ff2')
        w_speed_begin = local_weather.find('>', w_speed_zahl) + 1
        w_speed_end = local_weather.find('</p>', w_speed_zahl)
        w_speed = local_weather[w_speed_begin:w_speed_end]

        press_zahl = local_weather.find('head_ppp2')
        press_begin = local_weather.find('>', press_zahl) + 1
        press_end = local_weather.find('</p>', press_begin)
        press = local_weather[press_begin:press_end]

        results = {'condition': condition,
                   'temperature': temp,
                   'wind_dir': wind,
                   'wind_speed': w_speed,
                   'pressure': press
        }
        return results


class NasaSDOFilter(object):
    """Filters out interesting info from wetter24.de"""

    def filter(self, newtext):
        snippet_solar_begin = newtext.find('<h1>AIA 094, 335, 193</h1>')
        snippet_solar = newtext[snippet_solar_begin:newtext.find('latest_image', snippet_solar_begin) + 9]
        solar_img_begin = snippet_solar.find('href="') + 6
        solar_img_end = snippet_solar.find('">', solar_img_begin)
        solar_img = 'http://sdo.gsfc.nasa.gov' + snippet_solar[solar_img_begin:solar_img_end]

        return {'url_image_nasa_sdo': solar_img}


def siteScraper(url, interval, filter):
    """Constructs a sitescraper containing a SimpleClock, HTTPGetter and Filter"""

    return Pipeline(SimpleClock(interval),
                    HTTPGetter(url),
                    Filter(filter)
    )


weatherScraper = Graphline(
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

weatherScraper.run()