# -*- coding: utf-8 -*-
#
# Copyright 2014 Hackerfleet and Kamaelia Contributors(1)
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
# http://www.kamaelia.org/AUTHORS - please extend this file,
#     not this notice.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -------------------------------------------------------------------------

__author__ = 'riot'

import json
import time
import os

from Axon.Component import component
from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished
import cherrypy
from cherrypy import Tool
from bson import json_util

from hfos.utils.logger import log, debug, critical, error, warn


class WebGate(component):
    """Cherrypy based Web Gateway Component for user interaction."""
    # TODO: This design currently has one major design flaw:
    # The Webclient objects are not registered per client
    # As such the easiest way to discern what request's response goes to where,
    # a defer mechanism is used, that just stores the request url as reference.
    # This is not good, as multiple requests with the same url (but e.g. different post data)
    # may probably get lost or end up at strange places.
    # That may not be a problem because handling such data CAN still happen at a later point
    # (i.e. in the content generating router pipe)...
    # Still, this issue and having a webclient object that actually represents ONE client has to be
    # considered for various reasons, like security, authentication etc.

    #################### WebClient ####################

    class WebClient(threadedcomponent):
        def __init__(self, gateway):
            """
            Actual httpd-connected client component.
            """
            super(WebGate.WebClient, self).__init__()
            self.gateway = gateway
            self.timeout = gateway.timeout
            self.responses = {}

        @cherrypy.expose
        def default(self, *args):  # cherrypy needs the args, we don't
            """
            Accepts all client side requests and pushes them out of our gateway.
            To manage returning responses, a defer is created with this object as reference.
            The outbound message should be handled by a PipelineSelector equipped with a bunch of
            routes in the form of (RouteMatchConditionFunction, ResponseGeneratingPipeline).

            The router's pipelines will be created ad hoc and get the request sent in to their inbox
            by the PipeSelector.

            *** NOTICE ************************************************************
            Those pipes MUST finish in reasonable time, otherwise they get stopped
            and an unanswered request is the result!
            ***********************************************************************
            """

            recipient = cherrypy.request.path_info.lstrip("/")
            if not recipient:
                recipient = "index.html"
            request = cherrypy.request
            remote = request.remote
            log("[WC] Client ip: ", remote, lvl=debug)

            gotjson = False

            if 'Content-Length' in request.headers:
                # Seems we got something with a body

                clength = int(request.headers['Content-Length'])
                ctype = request.headers['Content-Type']
                log("[WC] Something with a body. Length: ", clength, lvl=debug)

                if not str(ctype).startswith('application/json'):  # '; charset=UTF-8':
                    log("[WC] Strange content type received!", lvl=error)
                    log("[WC] '%s': '%s'" % (ctype, request._get_dict), lvl=error)
                else:
                    log("[WC] Received json.", lvl=debug)
                    gotjson = True

                rawbody = b""
                body = ""
                decodedbody = ""

                try:
                    rawbody = cherrypy.request.body.read(int(clength))
                    decodedbody = bytes(rawbody).decode("UTF8")
                    log("[WC] Decoded successfully: ", decodedbody, lvl=debug)
                except (IOError, ValueError, TypeError):  # TODO: i certainly hope these are enough
                    log("[WC] Input decoding failure!", lvl=critical)
                    log("[WC] I was fed: '%s'" % rawbody)

                if clength > 0:
                    log("[WC] Length: '%i' Type: '%s'" % (int(clength), ctype), lvl=debug)

                    # try to convert http bytes to unicode json

                    try:
                        body = json.loads(decodedbody)
                        log("[WC] Decoded")
                    except ValueError:
                        log("[WC] JSON Decoding failed! Exception was: '%s'" % ValueError, lvl=error)
                        log("[WC] Tried to parse '%s'" % rawbody, lvl=debug)
                else:
                    log("[WC] No body content.")
                    body = None
            else:
                body = ""

            log("[WC] Client '%s' request to url: '%s'" % (remote.ip, recipient))

            #from pprint import pprint
            #pprint(request._get_dict())  # this little debugging helper is of mighty use

            msg = {'client': remote,
                   'recipient': recipient,
                   'request': request,
                   'body': body,
                   'timestamp': time.time(),
            }
            log("[WC] Inbound Message: ", msg, lvl=debug)
            self.gateway.transmit(msg, self)

            if gotjson:
                cherrypy.response.headers['Content-Type'] = 'application/json'
            # Store defer and wait for request's response
            return self.defer(msg, gotjson)

        def defer(self, request, respondjson=False):
            """
            Handles running defers with a timeout.
            (Probably unwise, since the PipeSelector (aka Router) already has one)
            See hfos.utils.selector.PipeSelector for more info.
            We can either remove it here or there
            """

            # Just looping around and wasting time is no good!
            while len(self.gateway.defers) > 0 and not request['recipient'] in self.responses:
                if request['timestamp'] + self.timeout < time.time():
                    log("[WC] Response timeout for '%s'. Cleaning up!" % request, lvl=warn)
                    del (self.gateway.defers[request['recipient']])
                    return json.dumps({'error': "No response!"})

                # Await response
                time.sleep(0.002)  # TODO: Hmm. Make this configurable, we'll probably need to tune.

            responseobject = self.responses[request['recipient']]

            # Clean up
            del (self.responses[request['recipient']])
            del (self.gateway.defers[request['recipient']])

            # Respond
            if respondjson:
                response = str(json.dumps(responseobject['response'], default=json_util.default)).encode("UTF8")
            else:
                response = responseobject['response']
            log("[WC] Delivering response for '%s'. Rendering time: %.0fms." % (request['recipient'],
                                                                                (time.time() - responseobject[
                                                                                    'timestamp']) * 1000))
            return response

    #################### /WebClient ####################


    def handle_response(self, msg):
        #log("[WG]DEBUG:Response received: '%s' Client References: '%s'" % (msg, self.defers))
        if msg['recipient'] in self.defers:
            client = self.defers[msg['recipient']]['ref']
            client.responses[msg['recipient']] = msg

    def transmit(self, msg, clientref):
        log("[WG] Transmitting on behalf of client '%s'" % clientref.name, lvl=debug)
        #log("[WG]DEBUG:Message:'%s'" % msg)
        self.defers[msg['recipient']] = {'ref': clientref, 'msg': str(msg)}
        self.send(msg, "outbox")

    def __init__(self, assetdir=None, enabled=True, timeout=30, port=8055):
        super(WebGate, self).__init__()

        self.debug = True
        self.port = port
        self.timeout = timeout  # Selector pipeline waiting time
        self.engine_enabled = enabled

        if not assetdir:
            self.assetdir = os.path.join(os.path.dirname(__file__), '../../assets')
        else:
            self.assetdir = assetdir

        log("[WG] Asset directory: ", assetdir)

        self.clients = []
        self.defers = {}  # Schema: {msg.recipient: {ref:clientref,msg:msg}}

    def main(self):
        if self.engine_enabled:
            self._start_engine()
        else:
            log("[WG] WebGate not enabled!", lvl=warn)

        finished = False
        while not finished:  # TODO: determine and ensure component lifetime
            while not self.anyReady():
                yield 1

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                #print("[WG] Data incoming:", data)
                #if len(self.defers) > 1:
                #    log("[WG] More than one defer running:", self.defers, lvl=warn)

                self.handle_response(data)

            if self.dataReady("control"):
                data = self.recv("control")
                if type(data) == producerFinished:
                    finished = True

            yield 1

    def _ev_client_connect(self):
        # TODO: Does probably not work anymore. Evaluate need and reintegrate.
        log("[WG] Client connected: '%s'" % cherrypy.request)
        self.clients.append(cherrypy.request)

    def _stop_engine(self):
        self.defers = {}
        cherrypy.engine.stop()
        return True  # TODO: Make sure we really stopped it..

    def _start_engine(self):
        # TODO: This needs cleanups and overhaul
        logger = cherrypy.log
        logger.logger_root = ''

        cherrypy.config.update({'server.socket_port': self.port,
                                'server.socket_host': '0.0.0.0'})

        if self.debug:
            log("[WG] Enabling autoreload mode for assetsdir '%s'" % self.assetdir, lvl=debug)

            for folder, subs, files in os.walk(self.assetdir):
                for filename in files:
                    cherrypy.engine.autoreload.files.add(filename)

        cherrypy.tools.clientconnect = Tool('on_start_resource', self._ev_client_connect)
        config = {
            '/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': self.assetdir},
            "/favicon.ico": {
                "tools.staticfile.on": True,
                "tools.staticfile.filename":
                    self.assetdir + "/icons/favicon.ico"
            },
        }

        # TODO: This construct probably needs a change towards ONE client object PER client, not one for all
        self.webclient = self.WebClient(self)

        cherrypy.tree.mount(self.webclient, "/", config=config)

        cherrypy.engine.start()
        log("[WG] Engine started")
        return True  # TODO: Make sure we really started it..
