#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__author__ = 'riot'

import os
import time

from Axon.Component import component
from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished, shutdownMicroprocess
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Util.TwoWaySplitter import TwoWaySplitter
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Collate import Collate
import jsonpickle, json
import cherrypy
from cherrypy import Tool

from bson import json_util

from pprint import pprint

from hfos.utils.templater import MakoTemplater
from hfos.utils.dict import WaitForDict
from hfos.utils.selector import PipeSelector
from hfos.database.mongo import MongoReader
from hfos.database.migration import crew, groups, sensordata
from hfos.logging import log, debug, warn

# TODO: Evaluate, the assets page Store
# * does it really still makes sense?
# * can this be done better?
endpoints = {'': {'redirect': "index.html"},
}

def registerEndpoint(path, content):
    endpoints[path] = content

class WebStore(component):

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) in (producerFinished, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False


    def main(self):
        while not self.finished():
            while not self.anyReady():
                self.pause()
                yield 1

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                endpoint, content = data
                log("WebStore: registering endpoint '%s'" % endpoint)

                registerEndpoint(endpoint, content)



class WebGate(component):
    """Cherrypy based Web Gateway Component for user interaction."""
    # TODO: This design currently has one major design flaw:
    # The Webclient objects are not registered per client
    # As such the easiest way to discern what request's response goes to where,
    # a defer mechanism is used, that just stores the request url as reference.
    # This is very bad, as multiple requests with the same url (but e.g. different post data)
    # will get lost or end up at strange places.
    # That may not be a problem because handling such data CAN still happen at a later point
    # (i.e. in the content generating router pipe)...
    # Still, this and having a webclient object that actually represents ONE client has to be
    # considered for various reasons, like security, authentication etc.

    #################### WebClient ####################

    class WebClient(threadedcomponent):
        def __init__(self, gateway):
            super(WebGate.WebClient, self).__init__()
            self.gateway = gateway
            self.endpoints = {}
            self.responses = {}

        @cherrypy.expose
        def default(self, *args):  # TODO: Whats *args doing here?
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
            body = cherrypy.request
            remote = body._get_dict()['remote']
            #log(body._get_dict().keys())

            log("[WC] Client '%s' request to url: '%s'" % (remote.ip, recipient))

            msg = {'client': remote,
                   'recipient': recipient,
                   'body': body,
                   'timestamp': time.time(),
            }

            self.gateway.transmit(msg, self)

            # Store defer and wait for request's response
            return self.defer(msg)

        #@cherrypy.tools.json_in()

        @cherrypy.expose
        def data(self, *args):
            """
            Should be doing pretty much the same thing, though de/encoding in json will be performed
            """
            # Inconveniently decode JSON back to an object.
            # Actually this should be managed by cherrpy and jQuery,
            # alas that prove difficult.
            # Suppose this should be the same for all calls to /rpc

            log("[WC] Client: ", args)
            cl = cherrypy.request.headers['Content-Length']
            rawbody = cherrypy.request.body.read(int(cl))
            # TODO: the actual request has to be worked up. Right now, we're just pushing back anything we get.

            recipient = cherrypy.request.path_info.lstrip("/")

            body = cherrypy.request
            remote = body._get_dict()['remote']

            log("[WC] Client '%s' RPC request to url: '%s'" % (remote.ip, recipient))
            log("[WC] Requestbody: ", body._get_dict(), lvl=debug)

            msg = {'client': remote,
                   'recipient': recipient,
                   'body': body,
                   'timestamp': time.time(),
            }

            self.gateway.transmit(msg, self)

            cherrypy.response.headers['Content-Type'] = 'application/json'

            # Store defer and wait for request's response
            return self.defer(msg, respondjson=True)


        def registerStaticEndpoint(self, path, content):
            # TODO: Unused, as of right now. Maybe it will serve some purpose?
            log("[WC] Registering assets endpoint: '%s'." % path)
            self.endpoints[path] = content
            return True

        def defer(self, request, respondjson=False):
            """
            Handles running defers with a timeout probably unwise, since the PipeSelector (aka Router)
            already has a timeout.
            Which is probably bad, see hfos.utils.selector.PipeSelector for more info.
            We can either remove it here or there, i think it makes sense to fix the pipes and the selector.
            """

            # Just looping around and wasting time is no good!
            while len(self.gateway.defers) > 0 and not request['recipient'] in self.responses:
                #log("[WC]:I'm still running with: '%s'" % request)

                if request['timestamp'] + 5 < time.time():
                    #log("[WC]WARN: Response timeout for '%s'. Cleaning up!" % request)
                    del (self.gateway.defers[request['recipient']])
                    return jsonpickle.encode({'error': "No response!"})

                # Await response
                time.sleep(0.002)

            responseobject = self.responses[request['recipient']]

            # Clean up
            del (self.responses[request['recipient']])
            del (self.gateway.defers[request['recipient']])

            if respondjson:
                response = str(json.dumps(responseobject['response'], default=json_util.default)).encode("UTF8")
            else:
                response = responseobject['response']
            log("[WC] Delivering response. Took '%f' seconds." % (time.time() - responseobject['timestamp']), lvl=debug)
            return response

    #################### /WebClient ####################


    def handleResponse(self, msg):
        #log("[WG]DEBUG:Response received: '%s' Client References: '%s'" % (msg, self.defers))
        if msg['recipient'] in self.defers:
            client = self.defers[msg['recipient']]['ref']
            client.responses[msg['recipient']] = msg

    def transmit(self, msg, clientref):
        log("[WG] Transmitting on behalf of client '%s'" % (clientref.name), lvl=debug)
        #log("[WG]DEBUG:Message:'%s'" % msg)
        self.defers[msg['recipient']] = {'ref': clientref, 'msg': str(msg)}
        self.send(msg, "outbox")

    def _registerEndpoint(self, path, content):
        log("[WG]: Endpoint registration on '%s'" % path)
        return self.webclient.registerStaticEndpoint(path=path, content=content)

    def __init__(self):
        super(WebGate, self).__init__()
        # TODO: Why no init args?
        self.debug = True
        self.port = 8055
        # TODO: Fix assets dir relativity over whole project
        self.assetdir = os.path.join(os.path.dirname(__file__), '../../assets')
        self.serverenabled = True

        self.clients = []
        self.defers = {}  # Schema: {msg.recipient: {ref:clientref,msg:msg}}

    def main(self):
        if self.serverenabled:
            self._start_Engine()
        else:
            log("[WG] WebGate not enabled!", lvl=warn)

        finished = False
        while not finished:  # TODO: determine and ensure component lifetime
            while not self.anyReady():
                yield 1

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                #print("[WG] Data incoming:", data)
                if len(self.defers) > 1:
                    log("[WG] More than one defer running:", self.defers, lvl=warn)

                self.handleResponse(data)

            if self.dataReady("control"):
                data = self.recv("control")
                if type(data) == producerFinished:
                    finished = True

            yield 1

    def _ev_client_connect(self):
        # TODO: Does probably not work anymore. Evaluate need and reintegrate.
        log("[WG] Client connected: '%s'" % cherrypy.request)
        self.clients.append(cherrypy.request)

    def _stop_Engine(self):
        self.defers = {}
        cherrypy.engine.stop()
        return True  # TODO: Make sure we really stopped it..

    def _start_Engine(self):
        # TODO: This needs cleanups and overhaul
        logger = cherrypy.log
        logger.logger_root = ''

        cherrypy.config.update({'server.socket_port': self.port,
                                'server.socket_host': '0.0.0.0',
        })

        if self.debug:
            log("[WG] Enabling autoreload mode for assetsdir '%s'" % self.assetdir, lvl=debug)

            for folder, subs, files in os.walk(self.assetdir):
                for filename in files:
                    log("[WG] Autoreload enabled for: '%s'" % str(filename), lvl=debug)
                    cherrypy.engine.autoreload.files.add(filename)

        cherrypy.tools.clientconnect = Tool('on_start_resource', self._ev_client_connect)
        config = {
            '/assets':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': self.assetdir},
        }

        # TODO: This construct probably needs a change towards ONE client object PER client, not one for all
        self.webclient = self.WebClient(self)

        cherrypy.tree.mount(self.webclient, "/", config=config)

        cherrypy.engine.start()
        return True  # TODO: Make sure we really started it..


# TODO: Move these to another sane place.

def build_staticTemplater():
    return Graphline(TS=TwoWaySplitter(),
                     CE=ConsoleEchoer(),
                     WFD=WaitForDict(['recipient', 'response']),
                     PT=PureTransformer(lambda x: {'response': MakoTemplater(template=x['recipient']).render(x)}),
                     linkages={("self", "inbox"): ("TS", "inbox"),
                               ("TS", "outbox"): ("PT", "inbox"),
                               ("TS", "outbox2"): ("WFD", "inbox"),
                               ("PT", "outbox"): ("WFD", "inbox"),
                               ("WFD", "outbox"): ("self", "outbox")
                     }
    )



def build_urls():
    """
    Builds the actual content building component generators and url filters in a way
    that a PipeSelector can work with.

    """

    def build_async_webpipe(pipe):
            rpcpipe = Graphline(
                PIPE=pipe,
                PT=PureTransformer(lambda x: {'response': x}),
                WFD=WaitForDict(['recipient', 'response']),
                linkages={("self", "inbox"): ("WFD", "inbox"),
                          ("PIPE", "outbox"): ("PT", "inbox"),
                          ("PT", "outbox"): ("WFD", "inbox"),
                          ("WFD", "outbox"): ("self", "outbox"),
                }
            )
            return rpcpipe


    def build_staticTemplates(templates):


        templfolder = "templates"
        routes = []
        #print(os.path.realpath(templfolder))
        import functools

        def testRecipient(data, recipient):
            return data['recipient'] == recipient

        for root, subFolders, files in os.walk(templfolder):
            for template in files:
                #print(template, os.path.basename(template))
                if template in templates:
                    #print file
                    cond = functools.partial(testRecipient, recipient=os.path.basename(template))

                    routes.append((cond, build_staticTemplater))
        return routes

    def build_navdispTemplater():
        # TODO: This is, as you can guess easily by the next import just a fake mockup but demonstrates how to get
        # relevant data and insert it into a Templater or do whatever with it

        import random

        navdispTemplater = Graphline(
            DS=DataSource([{'spd_over_grnd': random.randint(0, 25), 'true_course': random.randint(0, 359)}]),
            WFD=WaitForDict(['recipient', 'response']),
            PT=PureTransformer(lambda x: {'response': MakoTemplater(template="navdisplay.html").render(x)},
            ),
            CE=ConsoleEchoer(),
            linkages={("self", "inbox"): ("WFD", "inbox"),
                      ("self", "control"): ("CE", "inbox"),
                      ("DS", "outbox"): ("PT", "inbox"),
                      ("PT", "outbox"): ("WFD", "inbox"),
                      ("WFD", "outbox"): ("self", "outbox"),
            }
        )
        return navdispTemplater

    def build_crewlist():
        crew_list = Pipeline(DataSource([crew]),
                             MongoReader(),
                             Collate(),
                             PureTransformer(lambda x: {'sEcho': 1,
                                                         'iTotalRecords': len(x),
                                                         'iTotalDisplayRecords': len(x),
                                                         'aaData': x}),
        )
        return build_async_webpipe(crew_list)



    statics = ['index.html',
               'about.html',
               'crew_add.html',
               'crew_list.html',
               ]

    urls = build_staticTemplates(statics)

    pprint(urls)
    urls += [
        (lambda x: x['recipient'] == 'navdisplay.html', build_navdispTemplater),
        (lambda x: str(x['recipient']).startswith('data/crew/list'), build_crewlist),
        #(lambda x: str(x['recipient']).startswith("/assets/css"), build_scssParser)
    ]

    print("#"*23)
    pprint(urls)

    return urls

def build_404template():
    return Graphline(TS=TwoWaySplitter(),
                     CE=ConsoleEchoer(),
                     WFD=WaitForDict(['recipient', 'response']),
                     PT=PureTransformer(lambda x: {'response': MakoTemplater(template='errors/404.html').render(x)}),
                     linkages={("self", "inbox"): ("TS", "inbox"),
                               ("TS", "outbox"): ("PT", "inbox"),
                               ("TS", "outbox2"): ("WFD", "inbox"),
                               ("PT", "outbox"): ("WFD", "inbox"),
                               ("WFD", "outbox"): ("self", "outbox")
                     }
    )

def build_WebUI():
    """
    Constructs a WebUI consiting of WebGate with WebClients and a Router (PipeSelector) with the selector's
    components being defined by the build_urls() function.
    """

    gate = Graphline(WG=WebGate(),
                     ROUTER=PipeSelector(build_urls(), defaultpipe=build_404template),
                     linkages={("WG", "outbox"): ("ROUTER", "inbox"),
                               ("ROUTER", "outbox"): ("WG", "inbox")
                     }
    ).activate()