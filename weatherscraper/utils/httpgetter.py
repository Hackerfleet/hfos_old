#! /usr/bin/env python3


import urllib.request
import urllib.error
import socket
import time

from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished, shutdownMicroprocess

__author__ = 'riot'

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

    def __init__(self, proxy=False, useragent=False, timeout=30, postdata=None, extraheaders=None, realm=False,
                 username=False, password=False, decode=False):
        super(HTTPGetter, self).__init__()
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
                                     # TODO: Doesn't this need the URI?
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

        self.headers = headers

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def geturldata(self, url):
        """Gets the configured webpage and transmits it via outbox.
        """

        content = ""
        connection = None

        print("gettin url: '%s" % url)

        # Open connection
        try:
            request = urllib.request.Request(url=url, headers=self.headers)
            connection = urllib.request.urlopen(request, timeout=self.timeout)
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
            while not self.dataReady("inbox"):
                time.sleep(0.1)

            url = self.recv("inbox")

            urldata = self.geturldata(url)
            self.send(urldata, "outbox")

            time.sleep(0.1)  # We're threaded, so its safe to wait