__author__ = 'riot'

from Axon.Component import component
from Axon.Ipc import shutdownMicroprocess

import cherrypy
from cherrypy import Tool
#import jsonpickle
import os
import time
import types

from weatherscraper.logging import log


class WebGate(component):
    """Cherrypy based Web Gateway Component for user interaction."""

    directory_name = "WebGate"

    class WebClient(object):
        def __init__(self, gateway):
            self.gateway = gateway
            self.endpoints = {}
            self.responses = {}

            self.endpoints['404'] = "No document found."

        @cherrypy.expose
        def default(self, *args):
            """
            Loader deliverably to give clients our loader javascript.
            """
            path = cherrypy.request.path_info.lstrip("/")
            # self.gateway.loginfo("Client connected from '%s:%s'." % (cherrypy.request.remote.ip,
            #                                                         cherrypy.request.remote.port))
            log("Client request to '%s' from '%s'" % (path, cherrypy.request.remote.ip))

            #pprint(args)
            #self.gateway.logdebug(str(cherrypy.request.__dict__))

            if path in self.endpoints:
                #page = "<html>" + self.header + "<body>" + self.endpoints[path]() + "</body></html>"
                return self.endpoints[path]
            else:
                return self.endpoints['404']

        def registerEndpoint(self, path, content):
            log("Endpoint registered:", path)
            self.endpoints[path] = content
            return True

        # def defer(self, request):
        #     # TODO: Needs a timeout and error checking etc.
        #     # Just looping around and wasting time is no good!
        #     while len(self.gateway.defers) > 0 and not request.recipient in self.responses:
        #         self.gateway.loginfo("I'm still running.")
        #
        #         if request.timestamp + 0 < time.time():
        #             self.gateway.logwarning("Response timeout for '%s'. Cleaning up!" % request)
        #             del(self.gateway.defers[request.recipient])
        #             return jsonpickle.encode(request.response("No response!"))
        #
        #         # Await response
        #         time.sleep(1)
        #
        #     self.gateway.loginfo("Delivering response.")
        #     response = jsonpickle.encode(self.responses[request.recipient])
        #
        #     # Clean up
        #     del(self.responses[request.recipient])
        #     del(self.gateway.defers[request.recipient])
        #
        #     return response
        #
        # @cherrypy.expose
        # #@cherrypy.tools.json_in
        # def rpc(self):
        #     # Inconveniently decode JSON back to an object.
        #     # Actually this should be managed by cherrpy and jQuery,
        #     # alas that prove difficult.
        #     cl = cherrypy.request.headers['Content-Length']
        #     rawbody = cherrypy.request.body.read(int(cl))
        #     body = jsonpickle.decode(rawbody)
        #     recipient = body['recipient']
        #     func = body['func']
        #     arg = body['arg']
        #
        #     # Suppose this should be the same for all calls to /rpc
        #     cherrypy.response.headers['Content-Type'] = 'application/json'
        #
        #     # Replace simple directory addresses
        #     if recipient in self.gateway.directory:
        #         recipient = self.gateway.directory[recipient]
        #
        #     msg = Message(sender=self.gateway.name, recipient=recipient, func=func, arg=arg)
        #
        #     self.gateway.transmit(msg, self)
        #
        #     # Store defer and wait for request's response
        #     return self.defer(msg)
    #
    # def handleResponse(self, msg):
    #     self.logdebug("Response received: '%s' Client References: '%s'" % (msg, self.defers))
    #     if msg.sender in self.defers:
    #         self.loginfo("Storing deferred response for delivery.")
    #         client = self.defers[msg.sender]['ref']
    #         client.responses[msg.sender] = msg

    # def transmit(self, msg, clientref):
    #     self.logdebug("Transmitting on behalf of client '%s': '%s'" % (clientref, msg))
    #     self.defers[msg.recipient] = {'ref': clientref, 'msg':str(msg)}
    #     self.send(msg, "signal")


    def _registerEndpoint(self, path, content):
        return self.webclient.registerEndpoint(path=path, content=content)

    def __init__(self, debug=True, port=8055, serverenabled=True, staticdir=None):
        super(WebGate, self).__init__()

        self.debug = debug
        self.port = port
        self.serverenabled = serverenabled
        if not staticdir:
            self.staticdir = os.path.join(os.path.dirname(__file__), '../../static')
        else:
            self.staticdir = staticdir

        self.clients = []

        #self.defers = {} # Schema: {msg.recipient: {ref:clientref,msg:msg}}

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if type(msg) == shutdownMicroprocess:
                self.send(msg, "signal")
                return True
        return False

    def main(self):
        if self.serverenabled:
            self._start_Engine()

        while not self.finished():
            while not self.anyReady():
                self.pause()
                yield 1

            if self.dataReady("inbox"):
                data = self.recv("inbox")
                endpoint, content = data

                self.webclient.registerEndpoint(endpoint, content)


    def _ev_client_connect(self):
        log("Client request '%s'" % cherrypy.request)
        self.send(["CLIENT_CONNECT", cherrypy.request], "outbox")
        self.clients.append(cherrypy.request)


    def _stop_Engine(self):
        #self.defers = {}
        cherrypy.engine.stop()
        return True # TODO: Make sure we really stopped it..

    def _start_Engine(self):
        logger = cherrypy.log
        logger.logger_root = ''

        cherrypy.config.update({'server.socket_port': self.port,
                                'server.socket_host': '0.0.0.0',
                                })

        if self.debug:
            #self.loginfo("Enabling debug (autoreload) mode for staticdir '%s'" % self.staticdir)

            for folder, subs, files in os.walk(self.staticdir):
                for filename in files:
                    #self.logdebug("Autoreload enabled for: '%s'" % str(filename))
                    cherrypy.engine.autoreload.files.add(filename)

        cherrypy.tools.clientconnect = Tool('before_handler', self._ev_client_connect)
        config = {'/static':
                  {'tools.staticdir.on': True,
                   'tools.staticdir.dir': self.staticdir,
                   'tools.encode.on': False,
                   #'tools.encode.encoding': "utf-8"
                  }
                 }

        self.webclient = self.WebClient(gateway=self)

        cherrypy.tree.mount(self.webclient, "/", config=config)

        cherrypy.engine.start()
        return True # TODO: Make sure we really started it..

