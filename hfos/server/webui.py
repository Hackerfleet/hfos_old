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

#
# This is the first attempt at building a pipelined WebUI.
# Through experience, much of this is virtually outdated and will
# be rebuilt for the next release - hopefully 1.1.
# (This will include parts of Kamaelia's new WebGate)
#


__author__ = 'riot'

import os
import time

from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.DataSource import DataSource
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Util.TwoWaySplitter import TwoWaySplitter
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.Collate import Collate
from Kamaelia.Web.webgate import WebGate

from hfos.utils.templater import MakoTemplater
from hfos.utils.dict import WaitForDict
from hfos.utils.selector import PipeSelector
from hfos.utils.logger import Logger
from hfos.database.mongoadaptors import MongoReader, MongoFindOne, MongoUpdateOne, MongoTail
from hfos.database.mongo import crew, logbook, switches, routes
from hfos.utils.tilecache import Tilecache

from hfos.utils.logger import log, debug, warn, critical


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
        template_folder = "templates"
        template_routes = []
        #print(os.path.realpath(templfolder))
        import functools

        def test_recipient(data, recipient):
            return data['recipient'] == recipient

        for root, subFolders, files in os.walk(template_folder):
            for template in files:
                if template in templates:
                    cond = functools.partial(test_recipient, recipient=os.path.basename(template))

                    template_routes.append((cond, build_static_templater))
        return template_routes

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
            if 'uid' in data and 'name' in data:
                data['name'] = '<a href="crew/details/' + str(data['uid']) + '">' + data['name'] + '</a>'
            else:
                log("[CREW] List: Entry without uid/name found: '%s'" % data, lvl=warn)
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
            if 'no' in data:
                no = str(data['no'])
            else:
                log("[LOGBOOK] List: No id for entry found! '%s'" % data, lvl=warn)
                no = "NaN"
            data['no'] = '<a href="logbook/details/' + no + '">' + no + '</a>'
            return data

        def set_datetime(data):
            if 'time' in data:
                datestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['time']))
                data['time'] = datestr
            else:
                log("[LOGBOOK] List: No time for entry found! '%s'" % data, lvl=warn)
            return data

        crew_list = Pipeline(DataSource([logbook]),
                             MongoReader(),
                             PureTransformer(set_detail_link),
                             PureTransformer(set_datetime),
                             Logger(name="LOGBOOKLIST", level=debug),
                             Collate(),
                             PureTransformer(lambda x: {'sEcho': 1,
                                                        'iTotalRecords': len(x),
                                                        'iTotalDisplayRecords': len(x),
                                                        'aaData': x}
                             ),
        )
        return build_async_webpipe(crew_list)

    def build_logbook_latest():
        def get_logbook_subfield(request):

            try:
                return str(request['recipient']).lstrip('logbook/latest/')
            except:
                return None

        logbook_latest = Pipeline(PureTransformer(get_logbook_subfield),
                                  Logger(name="LOGBOOKLATEST", level=critical),
                                  MongoTail(logbook),
                                  PureTransformer(lambda x: {'response': x}),
                                  Logger(name="LOGBOOKLATEST", level=debug),
        )
        return build_sync_webpipe(logbook_latest)


    def build_crewdetails():
        def get_crew_id(request):
            try:
                return int(str(request['recipient']).lstrip('crew/details/'))
            except:
                return -1

        crew_details = Pipeline(PureTransformer(get_crew_id),
                                MongoFindOne('uid', crew),
                                Logger(name="CREWDETAILS", level=debug),
                                PureTransformer(
                                    lambda x: {'response': MakoTemplater(template="crew_add.html").render(x)}),
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

    def build_switchboard():
        switchboard = Pipeline(DataSource([switches]),
                               MongoReader(),
                               Collate(),
                               Logger(name="SWITCHBOARD", level=debug),
                               PureTransformer(
                                   lambda x: MakoTemplater(template="switchboard.html", usedict=False).render(x)),
                               Logger(name="SWITCHBOARD_OUTPUT", level=warn)
        )
        return build_async_webpipe(switchboard)

    def build_switch_handler():
        def get_switch_id(request):
            log(request['body'], lvl=critical)

            return int(str(request['recipient']).lstrip('switches/'))

        switch_handler = Pipeline(Logger(name="SWITCHCONTROL", level=debug),
        )
        return build_sync_webpipe(switch_handler)

    def build_route_service():
        def get_route_id(request):
            try:
                return int(str(request['recipient']).lstrip('route/get/'))
            except:
                return -1

        def build_get():
            route_details = Pipeline(PureTransformer(get_route_id),
                                     MongoFindOne('id', routes),
                                     Logger(name="ROUTE-GET", level=debug),
                                     PureTransformer(
                                         lambda x: {'response': x}),
            )
            return build_sync_webpipe(route_details)

        def build_store():
            route_details = Pipeline(PureTransformer(lambda x: x['body']),
                                     Logger(name="ROUTE-STORE-OBJ", level=critical),
                                     MongoUpdateOne(routes),
                                     Logger(name="ROUTE-STORE-RES", level=critical),
                                     PureTransformer(
                                         lambda x: {'response': x}),
            )
            return build_sync_webpipe(route_details)


        actions = [
            (lambda x: str(x['recipient']).startswith('route/get/'), build_get),
            (lambda x: str(x['recipient']).startswith('route/store/'), build_store),
        ]
        router = PipeSelector(routes=actions)
        return router

    def build_Tilecache():
        return Tilecache()

    statics = ['index.html',
               'about.html',
               'navigation.html',
               'communication.html',
               'settings.html',
               'crew_add.html',
               'crew_list.html',
               'logbook.html',
    ]

    urls = build_static_templates(statics)
    urls += [
        (lambda x: x['recipient'].startswith('tiles/'), build_Tilecache),
        (lambda x: x['recipient'] == 'navdisplay.html', build_navdisp_templater),
        (lambda x: x['recipient'] == 'switchboard.html', build_switchboard),
        (lambda x: str(x['recipient']).startswith('switches/'), build_switch_handler),
        (lambda x: str(x['recipient']).startswith('crew/list'), build_crewlist),
        (lambda x: str(x['recipient']).startswith('crew/details'), build_crewdetails),
        (lambda x: str(x['recipient']).startswith('crew/store'), build_crewstore),
        (lambda x: str(x['recipient']).startswith('logbook/list'), build_logbook_list),
        (lambda x: str(x['recipient']).startswith('logbook/latest'), build_logbook_latest),
        (lambda x: str(x['recipient']).startswith('route/'), build_route_service),
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

    gate = Graphline(WG=WebGate(assetdir=os.path.abspath("assets")),
                     ROUTER=PipeSelector(build_urls(), defaultpipe=build_404template),
                     linkages={("WG", "outbox"): ("ROUTER", "inbox"),
                               ("ROUTER", "outbox"): ("WG", "inbox")
                     }
    )
    gate.activate()