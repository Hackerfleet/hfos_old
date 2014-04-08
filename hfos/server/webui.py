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
import json

from Axon.Component import component
from Axon.ThreadedComponent import threadedcomponent
from Axon.Ipc import producerFinished
from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Util.TwoWaySplitter import TwoWaySplitter
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Collate import Collate
import jsonpickle
import cherrypy
from cherrypy import Tool
from bson import json_util

from hfos.utils.templater import MakoTemplater
from hfos.utils.dict import WaitForDict
from hfos.utils.selector import PipeSelector
from hfos.utils.logger import Logger
from hfos.database.mongo import MongoReader, MongoFindOne, MongoUpdateOne
from hfos.database.migration import crew, logbook
from hfos.utils.logger import log, debug, warn, error, critical


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

                clength = request.headers['Content-Length']
                ctype = request.headers['Content-Type']
                log("[WC] Length: '%i' Type: '%s'" % (int(clength), ctype), lvl=debug)

                if not str(ctype).startswith('application/json'):  # '; charset=UTF-8':
                    log("[WC] Strange content type received!", lvl=error)
                    log("[WC] '%s': '%s'" % (ctype, request._get_dict), lvl=error)
                else:
                    gotjson = True

                rawbody = b""
                decodedbody = ""
                body = ""

                # try to convert http bytes to unicode json
                try:
                    rawbody = cherrypy.request.body.read(int(clength))
                    decodedbody = bytes(rawbody).decode("UTF8")
                except (IOError, ValueError, TypeError):  # TODO: i certainly hope these are enough
                    log("[WC] Input decoding failure!", lvl=critical)
                    log("[WC] I was fed: '%s'" % rawbody)

                try:
                    body = json.loads(decodedbody)
                except ValueError:
                    log("[WC] JSON Decoding failed! Exception was: '%s'" % ValueError, lvl=error)
                    log("[WC] Tried to parse '%s'" % rawbody, lvl=debug)
                cherrypy.response.headers['Content-Type'] = 'application/json'
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

            self.gateway.transmit(msg, self)

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
                if request['timestamp'] + 5 < time.time():
                    log("[WC] Response timeout for '%s'. Cleaning up!" % request, lvl=warn)
                    del (self.gateway.defers[request['recipient']])
                    return jsonpickle.encode({'error': "No response!"})

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
                                                                     (time.time() - responseobject['timestamp'])*1000))
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
                if len(self.defers) > 1:
                    log("[WG] More than one defer running:", self.defers, lvl=warn)

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
                    log("[WG] Autoreload enabled for: '%s'" % str(filename), lvl=debug)
                    cherrypy.engine.autoreload.files.add(filename)

        cherrypy.tools.clientconnect = Tool('on_start_resource', self._ev_client_connect)
        config = {
            '/assets': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': self.assetdir},
        }

        # TODO: This construct probably needs a change towards ONE client object PER client, not one for all
        self.webclient = self.WebClient(self)

        cherrypy.tree.mount(self.webclient, "/", config=config)

        cherrypy.engine.start()
        return True  # TODO: Make sure we really started it..


# TODO: Move these to another sane place.

def build_static_templater():
    return Graphline(TS=TwoWaySplitter(),
                     CE=ConsoleEchoer(),
                     WFD=WaitForDict(['recipient', 'response']),
                     PT=PureTransformer(lambda x: {'response': MakoTemplater(template=x['recipient']).render(x)}),
                     linkages={("self", "inbox"): ("TS", "inbox"),
                               ("TS", "outbox"): ("PT", "inbox"),
                               ("TS", "outbox2"): ("WFD", "inbox"),
                               ("PT", "outbox"): ("WFD", "inbox"),
                               ("WFD", "outbox"): ("self", "outbox")})


def build_urls():
    """
    Builds the actual content building component generators and url filters in a way
    that a PipeSelector can work with.

    """

    def build_sync_webpipe(pipe, name=""):
        """
        Constructs a webpipe that does care for browser supplied input.
        """

        rpcpipe = Graphline(
            TS=TwoWaySplitter(),
            PIPE=pipe,
            #PT=PureTransformer(lambda x: {'response': x}),
            WFD=WaitForDict(['recipient', 'response']),
            linkages={("self", "inbox"): ("TS", "inbox"),
                      ("TS", "outbox"): ("WFD", "inbox"),
                      ("TS", "outbox2"): ("PIPE", "inbox"),
                      ("PIPE", "outbox"): ("WFD", "inbox"),
                      #("PT", "outbox"): ("WFD", "inbox"),
                      ("WFD", "outbox"): ("self", "outbox")})
        if name:
            rpcpipe.name = name
        return rpcpipe

    def build_async_webpipe(pipe):
        """
        Constructs a webpipe that doesn't care for browser supplied input.
        """

        rpcpipe = Graphline(
            PIPE=pipe,
            PT=PureTransformer(lambda x: {'response': x}),
            WFD=WaitForDict(['recipient', 'response']),
            linkages={("self", "inbox"): ("WFD", "inbox"),
                      ("PIPE", "outbox"): ("PT", "inbox"),
                      ("PT", "outbox"): ("WFD", "inbox"),
                      ("WFD", "outbox"): ("self", "outbox")})
        return rpcpipe

    def build_static_templates(templates):
        """
        Finds all static templates and generates routing rules for them
        """

        # TODO: Fix this folder, everywhere... *sigh*
        templfolder = "templates"
        routes = []
        #print(os.path.realpath(templfolder))
        import functools

        def test_recipient(data, recipient):
            return data['recipient'] == recipient

        for root, subFolders, files in os.walk(templfolder):
            for template in files:
                if template in templates:
                    cond = functools.partial(test_recipient, recipient=os.path.basename(template))

                    routes.append((cond, build_static_templater))
        return routes

    def build_navdisp_templater():
        # TODO: This is - as you can guess easily by the next import - just a fake mockup, but demonstrates how to get
        # relevant data and insert it into a Templater or do whatever with it

        import random

        navdisp_templater = Graphline(
            DS=DataSource([{'spd_over_grnd': random.randint(0, 25), 'true_course': random.randint(0, 359)}]),
            WFD=WaitForDict(['recipient', 'response']),
            PT=PureTransformer(lambda x: {'response': MakoTemplater(template="navdisplay.html").render(x)}),
            linkages={("self", "inbox"): ("WFD", "inbox"),
                      ("DS", "outbox"): ("PT", "inbox"),
                      ("PT", "outbox"): ("WFD", "inbox"),
                      ("WFD", "outbox"): ("self", "outbox")})
        return navdisp_templater

    def build_crewlist():
        def set_detail_link(data):
            data['name'] = '<a href="crew/details/'+str(data['uid'])+'">' + data['name'] + '</a>'
            return data

        crew_list = Pipeline(DataSource([crew]),
                             MongoReader(),
                             PureTransformer(set_detail_link),
                             Logger(name="CREWLIST", level=debug),
                             Collate(),
                             PureTransformer(lambda x: {'sEcho': 1,
                                                        'iTotalRecords': len(x),
                                                        'iTotalDisplayRecords': len(x),
                                                        'aaData': x}
                             ),
        )
        return build_async_webpipe(crew_list)

    def build_logbook_list():
        def set_detail_link(data):
            data['no'] = '<a href="crew/details/'+str(data['uid'])+'">' + data['no'] + '</a>'
            return data

        crew_list = Pipeline(DataSource([logbook]),
                             MongoReader(),
                             PureTransformer(set_detail_link),
                             Logger(name="LOGBOOKLIST", level=debug),
                             Collate(),
                             PureTransformer(lambda x: {'sEcho': 1,
                                                        'iTotalRecords': len(x),
                                                        'iTotalDisplayRecords': len(x),
                                                        'aaData': x}
                             ),
        )
        return build_async_webpipe(crew_list)


    def build_crewdetails():
        def get_crew_id(request):
            try:
                return int(str(request['recipient']).lstrip('crew/details/'))
            except:
                return -1

        crew_details = Pipeline(PureTransformer(get_crew_id),
                             MongoFindOne('uid', crew),
                             Logger(name="CREWDETAILS", level=debug),
                             PureTransformer(lambda x: {'response': MakoTemplater(template="crew_add.html").render(x)}),
        )
        return build_sync_webpipe(crew_details)

    def build_crewstore():
        def get_crew_id(request):
            log(request['body'], lvl=critical)

            return int(str(request['recipient']).lstrip('crew/store/'))

        crew_store = Pipeline(Logger(name="CREWSTORE INPUT", level=debug),
                              PureTransformer(lambda x: x['body']),
                              MongoUpdateOne(crew),
                             #Collate(),
                             Logger(name="CREWDETAILS DATA", level=debug),
                             PureTransformer(lambda x: {'response': x}),
                             Logger(name="CREWDETAILS PAGE", level=debug),
        )
        return build_sync_webpipe(crew_store)


    statics = ['index.html',
               'about.html',
               'navigation.html',
               'communication.html',
               'settings.html',
               'crew_add.html',
               'crew_list.html',
               'logbook.html']

    urls = build_static_templates(statics)
    urls += [
        (lambda x: x['recipient'] == 'navdisplay.html', build_navdisp_templater),
        (lambda x: str(x['recipient']).startswith('crew/list'), build_crewlist),
        (lambda x: str(x['recipient']).startswith('crew/details'), build_crewdetails),
        (lambda x: str(x['recipient']).startswith('crew/store'), build_crewstore),
        (lambda x: str(x['recipient']).startswith('logbook/list'), build_logbook_list),
    ]

    return urls


def build_404template():
    return Graphline(TS=TwoWaySplitter(),
                     WFD=WaitForDict(['recipient', 'response']),
                     PT=PureTransformer(lambda x: {'response': MakoTemplater(template='errors/404.html').render(x)}),
                     linkages={("self", "inbox"): ("TS", "inbox"),
                               ("TS", "outbox"): ("PT", "inbox"),
                               ("TS", "outbox2"): ("WFD", "inbox"),
                               ("PT", "outbox"): ("WFD", "inbox"),
                               ("WFD", "outbox"): ("self", "outbox")
                     }
    )


def build_webui():
    """
    Constructs a WebUI consiting of WebGate with WebClients and a Router (PipeSelector) with the selector's
    components being defined by the build_urls() function.
    """

    gate = Graphline(WG=WebGate(),
                     ROUTER=PipeSelector(build_urls(), defaultpipe=build_404template),
                     linkages={("WG", "outbox"): ("ROUTER", "inbox"),
                               ("ROUTER", "outbox"): ("WG", "inbox")
                     }
    )
    gate.activate()