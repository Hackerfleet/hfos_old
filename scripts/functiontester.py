__author__ = 'riot'

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector
from Kamaelia.Visualisation.Axon.AxonVisualiserServer import text_to_token_lists, AxonVisualiser

from weatherscraper.components import build_system

from weatherscraper.server.webui import build_WebUI

from weatherscraper.utils.selector import testPipeSelector

if __name__ == '__main__':
    #weatherScraper()
    #build_system(online=False, debug=True)
    build_WebUI()

    #Pipeline(Introspector(),
    #         text_to_token_lists(),
    #         AxonVisualiser(),
    #)#.activate()

    scheduler.run.runThreads()