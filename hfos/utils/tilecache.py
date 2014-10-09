#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

__author__ = 'riot'
__copyright__ = "Copyright 2011-2014, Hackerfleet Community"
__license__ = "GPLv3"
__status__ = "Beta"

import urllib.request
import urllib.error
import socket

import os.path
from os import makedirs
from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess

from hfos.utils.logger import log, debug


class Tilecache(component):
    Inboxes = {"inbox": "Items",
               "control": "Shutdown signalling",
    }
    Outboxes = {"outbox": "Items tagged with a sequence number, in the form (seqnum, item)",
                "signal": "Shutdown signalling",
    }

    def __init__(self, cachedir='/tmp/hfos-tilecache', defaulttile="",
                 proxy=False, useragent=False, timeout=30, postdata=None,
                 extraheaders=None, realm=False,
                 username=False, password=False, decode=False):
        super(Tilecache, self).__init__()
        self.proxy = proxy
        self.useragent = useragent
        self.timeout = timeout
        self.postdata = postdata
        self.decode = decode

        defaulttilefile = open(defaulttile, "rb")
        self.defaulttile = defaulttilefile.read()
        defaulttilefile.close()

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

        self.cachedir = cachedir


        # TODO:
        # ? Add layer lookup
        # # Add new caching layers to navigation.js
        # * Extrapolate filename from URL
        # * Check if tile is in cache
        #  * Get tile from cache
        # * Get tile from url
        #  * Store tile in cache
        # * Generate response with tile
        # * Make sure
        #   * tilecache directories exist and are writeable
        #   * Disk space is sufficient
        # * Add cache cleaning policy/means
        # * Add ability to toggle caching
        # * Give possibility to see what is cached
        # * ???

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def get_tile(self, url):

        log("Getting tile: ", url, lvl=debug)
        connection = None

        try:
            request = urllib.request.Request(url=url, headers=self.headers)
            connection = urllib.request.urlopen(request, timeout=self.timeout)
        except (urllib.error.ContentTooShortError,
                urllib.error.HTTPError,
                urllib.error.URLError,
                socket.timeout,
                UnicodeEncodeError,
                UnicodeDecodeError) as e:
            log("[TC] Tilegetter error: ", [type(e), e])

        content = None

        # Read and return requested content
        if connection:
            try:
                content = connection.read()
            except (socket.timeout, socket.error) as e:
                log("[TC] Tilegetter error: ", [type(e), e])

            connection.close()

        return content


    def main(self):
        """Main loop."""

        while not self.finished():
            while not self.dataReady("inbox"):
                self.pause()
                yield 1
            value = self.recv("inbox")

            # 'http://localhost:8055/tiles/tile.osm.org/{z}/{x}/{y}.png';
            # 'http://localhost:8055/tiles/tiles.openseamap.org/seamark/{z}/{x}/{y}.png';

            #log("[TC] Request:", value, lvl=error)
            spliturl = value['recipient'].split("/")
            #log("[TC] URL split", spliturl)
            service = "/".join(spliturl[1:-3])  # get all but the coords as service
            x = spliturl[-3]
            y = spliturl[-2]
            z = spliturl[-1].split('.')[0]

            filename = os.path.join(self.cachedir, service, x, y) + "/" + z + ".png"
            url = "http://" + service + "/" + x + "/" + y + "/" + z + ".png"
            #log("[TC] Estimated filename: ", filename, lvl=error)
            #log("[TC] Estimated URL: ", url, lvl=error)

            # TODO: Clean up, restructure this

            if os.path.isfile(filename):
                log("[TC] Tile in cache")

                tilefile = open(filename, "rb")
                tile = tilefile.read()
                value['response'] = tile
                tilefile.close()

            else:
                tile = self.get_tile(url)
                value['response'] = tile

                tilepath = os.path.dirname(filename)

                if tile:
                    try:
                        log("[TC] Caching tile...")
                        makedirs(tilepath, exist_ok=True)
                        tilefile = open(filename, "wb")
                        tilefile.write(tile)

                        tilefile.close()
                    except Exception as e:
                        log("[TC] Badass error: ", [type(e), e])
                else:
                    log("[TC] Got no tile, serving defaulttile.", lvl=debug)
                    value['response'] = self.defaulttile

            self.send(value, "outbox")
            yield 1


def testTilecache():
    tc = Tilecache()

