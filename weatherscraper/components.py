#! /usr/bin/python

__author__ = 'riot'

import time
import urllib.request
import urllib.error
import socket

from Axon.Ipc import producerFinished, shutdownMicroprocess
from Axon.ThreadedComponent import threadedcomponent
from Axon.Component import component
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Util.Clock import CheapAndCheerfulClock as SimpleClock
from Kamaelia.Util.Console import ConsoleEchoer


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


class WeatherFilter(component):
    """
    
    """

    Inboxes = {
        "inbox": "Messages to be passed through",
        "control": "Shutdown signalling",
    }
    Outboxes = {
        "outbox": "Passed through messages",
        "signal": "Shutdown signalling",
    }

    def __init__(self):
        """\
        """
        super(WeatherFilter, self).__init__()


    def main(self):
        """\
        """
        shutdown = False

        while not shutdown:
            print("Cycling")
            while not self.anyReady():
                yield 1

            if self.dataReady("inbox"):
                print("Incoming")

                data = self.recv("inbox")

                print("Filtering")

                local_weather = data[data.find('head_ww'):data.find('hPa<') + 4]

                condition_zahl = local_weather.find('head_ww')
                condition_begin = local_weather.find('alt="', condition_zahl) + 5
                condition_end = local_weather.find('"', condition_begin)
                condition = local_weather[condition_begin:condition_end]

                #print(condition)

                snippet_solar_begin = data.find('<h1>AIA 094, 335, 193</h1>')
                snippet_solar = data[snippet_solar_begin:data.find('latest_image', snippet_solar_begin) + 9]

                #print(snippet_solar)

                self.send(condition + snippet_solar)
                yield 1

            time.sleep(0.1)

            if self.dataReady("control"):
                shutdown = True

        for msg in self.Inbox("control"):
            self.send(msg, "signal")


weatherScraper = Graphline(W24=HTTPGetter(url="http://www.wetter24.de/wetter/berlin-alexanderplatz/10389.html"),
                           N=HTTPGetter(url="http://sdo.gsfc.nasa.gov/data/"),
                           W24C=SimpleClock(5),
                           NC=SimpleClock(10),
                           FILTER=WeatherFilter(),
                           CE=ConsoleEchoer(),
                           linkages={
                               ("W24C", "outbox"): ("W24", "inbox"),
                               ("NC", "outbox"): ("N", "inbox"),
                               ("W24", "outbox"): ("FILTER", "inbox"),
                               ("N", "outbox"): ("FILTER", "inbox"),
                               ("FILTER", "outbox") : ("CE", "inbox")
                           }
)

weatherScraper.run()
